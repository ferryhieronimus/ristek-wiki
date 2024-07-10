from datetime import datetime, UTC, timedelta
import os
import typing
import requests
import logging

from urllib.parse import urlencode
from pathlib import Path
from jose import jwt

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles

from config.config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
    JWT_SECRET,
    BASE_URL,
    DEPLOYED_ON_VERCEL,
)


app = FastAPI(docs_url=None, redoc_url=None)

# path to the docs, which we shall protect
PathLike = typing.Union[str, "os.PathLike[str]"]

# the security function
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/api/v1/auth/google")
async def login_google():
    query_params = urlencode(
        {
            "response_type": "code",
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "scope": "email",
            "access_type": "offline",
            "prompt": "select_account",
        }
    )

    authorization_url = f"https://accounts.google.com/o/oauth2/auth?{query_params}"
    return RedirectResponse(url=authorization_url)


@app.get("/api/v1/oauth2/callback/google")
async def auth_google(code: str):
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    try:
        # get the access token from google
        response = requests.post(
            "https://accounts.google.com/o/oauth2/token", data=data
        )
        response.raise_for_status()

        token_response = response.json()
        access_token = token_response.get("access_token")

        # get the user info from google
        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_info.raise_for_status()
        user_info_data = user_info.json()

        # check if the email is a valid ristek email
        if not user_info_data["email"].endswith("@ristek.cs.ui.ac.id"):
            return {"error": "Invalid email, must be a ristek email"}

        # generate our jwt token
        jwt_token = jwt.encode(
            {
                "sub": user_info_data["sub"],
                "email": user_info_data["email"],
                "exp": datetime.now(UTC) + timedelta(days=1),
            },
            JWT_SECRET,
        )

        # redirect to the docs homepage
        homepage_url = f"{BASE_URL}/docs/"
        response = RedirectResponse(url=homepage_url)
        response.set_cookie(key="token", value=jwt_token, httponly=True)

        return response

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to authenticate: {str(e)}")


class ProtectStaticFiles(StaticFiles):
    """
    Protects static files by checking for a valid token in the request cookies.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def __call__(self, scope, receive, send) -> None:
        assert scope["type"] == "http"
        request = Request(scope, receive)
        token = request.cookies.get("token")

        login_url = f"{BASE_URL}/api/v1/auth/google"
        response = RedirectResponse(url=login_url)

        # believed to be an unauthenticated user
        if not token:
            await response(scope, receive, send)
            return
        else:
            try:
                jwt.decode(token, JWT_SECRET)
            except jwt.ExpiredSignatureError:
                response.delete_cookie(key="token")
                await response(scope, receive, send)
                return
            except HTTPException:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # only authenticated users can access the docs
        await super().__call__(scope, receive, send)


# html=True to serve index.html files without to append /<markdown-filename>.html to the url
app.mount(
    "/docs",
    ProtectStaticFiles(
        directory="site", html=True
    ),
    name="Mkdocs Generated HTMLs",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
