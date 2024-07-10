import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = BASE_URL + "/api/v1/oauth2/callback/google"
JWT_SECRET = os.getenv("JWT_SECRET")
DEPLOYED_ON_VERCEL = (
    True
    if os.getenv("DEPLOYED_ON_VERCEL") == "1"
    or os.getenv("DEPLOYED_ON_VERCEL") == "True"
    or os.getenv("DEPLOYED_ON_VERCEL") == "true"
    else False
)
