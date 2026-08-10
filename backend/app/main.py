from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes_game import router as games_router
from app.api.routes_player import router as players_router
from app.db import create_db_and_tables

app = FastAPI(title="Mahoraga", version="0.5.0")
app.include_router(players_router)
app.include_router(games_router)


@app.on_event("startup")
def startup() -> None:
    create_db_and_tables()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="web")
