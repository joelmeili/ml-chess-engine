import chess

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from engine.engine import get_best_move
from engine.registry import ENGINES

from pathlib import Path
from fastapi.staticfiles import StaticFiles

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI()

class MoveRequest(BaseModel):
    fen: str
    engine: str
    time_limit: float = Field(default = 3.0, gt = 0, le = 10)

class MoveResponse(BaseModel):
    move: str | None

@app.get("/engines")
def list_engines():
    return [{"id": engine_id, "name": engine_info["name"]} for engine_id, engine_info in ENGINES.items()]

@app.post("/move")
def engine_move(request: MoveRequest) -> MoveResponse:
    if request.engine not in ENGINES:
        raise HTTPException(status_code = 400, detail = "Unknown engine")

    try:
        board = chess.Board(request.fen)

    except ValueError:
        raise HTTPException(status_code = 400, detail = "Invalid FEN")

    if not board.is_valid():
        raise HTTPException(status_code = 400, detail = "Invalid position")

    move = get_best_move(board, time_limit = request.time_limit, evaluate_fn = ENGINES[request.engine]["evaluate_fn"])

    return MoveResponse(move = move)

app.mount("/", StaticFiles(directory = STATIC_DIR, html = True), name = "static")