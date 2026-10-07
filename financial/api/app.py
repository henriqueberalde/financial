from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from financial.api.routes import categories, overview, spending, trends

WEB_DIR = Path(__file__).parent.parent / "web"


def create_app() -> FastAPI:
    app = FastAPI(title="financial")

    for route in (overview, spending, trends, categories):
        app.include_router(route.router, prefix="/api")

    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")

    return app
