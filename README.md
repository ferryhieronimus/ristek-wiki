# RISTEK WIKI 📖

Ristek Wiki serves as a documentation repository for RISTEK products and engineering guidelines.

## Overview

### Usage

All documentations are written in Markdown under the `docs/` directory. Adding a new wiki page is as simple as adding a new Markdown document under the `docs/` directory. You can add your own sub-directories if you want to group certain pages and its assets based on a topic.

### How it works

After searching through a myriad of ways to build and store wiki pages, we decided to go with the simplest and easily available option: GitHub as the storage. We write them in Markdown as it's an easy and pretty standard format for writing documentation.

Just using GitHub is simple enough but it makes navigating and searching for pages a bit tedious. The repository is also private so for RISTEK members without access to our GitHub, they can't open it. To tackle this, we decided to use MkDocs to build static HTML, CSS, and JS files from the Markdown files and serve them as a website on Vercel.

Using this method means exposing all the pages into the public without restrictions. This wiki is for internal purposes so we don't want to expose them just like that. To solve this, we used FastAPI to serve the static files built by MkDocs and add OAuth-based authentication to the site using Google. We restrict access only for RISTEK emails on the Google OAuth client settings. This way we can use our previous method of serving documentation as static files.

## Development

### Installation

Create a virtual environment and activate it

```bash
python -m venv env

# For POSIX/Unix Platforms
source env/bin/activate

# For Windows Cmd
env\Scripts\activate.bat 

# For Windows Powershell
env\Scripts\Activate.ps1
```

Install the dependencies

```bash
pip install -r requirements.txt
```

### Editing a page and viewing with hot reload

Run the following command if you want to just view the documentations. MkDocs will convert them into a site which you can view locally with hot reload. This is suitable to quickly see how a page will look when you're editing them.

```bash
mkdocs serve
```

MkDocs will serve the site at `http://127.0.0.1:8000`.

### Building the pages

If you want to create a static build of the documentation, you can run

```bash
mkdocs build
```

### Serving the pages

To serve the static files via FastAPI and have the authentication guard be activated, run this after you build the static files

```bash
python main.py
```

You can access the site on `${BASE_URL}/`.
