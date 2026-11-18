import chess
import pytest
from fastapi.testclient import TestClient

from engine.registry import ENGINES
from web.server import app

client = TestClient(app)

WHITE_IS_CHECKMATED = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
MISSING_BLACK_KING = "8/8/8/8/8/8/8/4K3 w - - 0 1"

def request_move(fen = chess.STARTING_FEN, engine = "pst", time_limit = 0.1):
    return client.post("/move", json = {"fen": fen, "engine": engine, "time_limit": time_limit})

def test_lists_all_engines():
    response = client.get("/engines")
    assert response.status_code == 200
    ids = {engine["id"] for engine in response.json()}
    assert ids == set(ENGINES)

@pytest.mark.parametrize("engine_id", list(ENGINES))
def test_every_engine_returns_legal_move(engine_id):
    response = request_move(engine=engine_id)
    assert response.status_code == 200
    move = chess.Move.from_uci(response.json()["move"])
    assert move in chess.Board().legal_moves

def test_returns_null_when_game_is_over():
    response = request_move(fen = WHITE_IS_CHECKMATED)
    assert response.status_code == 200
    assert response.json()["move"] is None

def test_unknown_engine_is_rejected():
    assert request_move(engine="does-not-exist").status_code == 400

def test_malformed_fen_is_rejected():
    assert request_move(fen = "hello").status_code == 400

def test_impossible_position_is_rejected():
    assert request_move(fen = MISSING_BLACK_KING).status_code == 400

@pytest.mark.parametrize("time_limit", [0, -1, 100])
def test_out_of_range_time_limit_is_rejected(time_limit):
    assert request_move(time_limit = time_limit).status_code == 422