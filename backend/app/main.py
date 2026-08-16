from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes_adaptation import router as adaptation_router
from app.api.routes_game import router as games_router
from app.api.routes_player import router as players_router
from app.api.routes_system import router as system_router
from app.chess_engine.engine_wrapper import EngineWrapper
from app.db import create_db_and_tables

app = FastAPI(title="Mahoraga", version="0.5.0")


@app.on_event("startup")
def startup() -> None:
    create_db_and_tables()
    try:
        app.state.engine = EngineWrapper()
    except FileNotFoundError:
        app.state.engine = None


@app.on_event("shutdown")
def shutdown() -> None:
    engine = getattr(app.state, "engine", None)
    if engine is not None:
        engine.close()


def get_engine():
    """Shared Stockfish for the app's lifetime - avoids spawning a fresh
    process per move. Falls back to a per-request engine if startup failed."""
    engine = getattr(app.state, "engine", None)
    if engine is not None:
        return engine
    return EngineWrapper()


app.include_router(players_router)
app.include_router(games_router)
app.include_router(adaptation_router)
app.include_router(system_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="web")
