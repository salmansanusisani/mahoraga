import chess

from app.adaptation.loss_localizer import LossPoint
from app.adaptation.signature_extractor import extract_signature


def _loss_point(fen: str, uci: str, loser: chess.Color, swing: float = 400.0) -> LossPoint:
    board = chess.Board(fen)
    move = chess.Move.from_uci(uci)
    assert move in board.legal_moves, (fen, uci)
    return LossPoint(
        ply=0,
        board_before=board,
        move=move,
        eval_before=0.0,
        eval_after=-swing if loser == chess.BLACK else swing,
        swing_against_loser=swing,
        loser_color=loser,
    )


def test_fork_detected() -> None:
    sig = extract_signature(_loss_point("3q1r1k/8/8/8/3N4/8/8/6K1 w - - 0 1", "d4e6", chess.BLACK))
    assert "fork" in sig.motifs
    assert sig.phenomenon == "fork"


def test_pin_detected() -> None:
    sig = extract_signature(_loss_point("4k3/8/2n5/8/8/8/8/5B1K w - - 0 1", "f1b5", chess.BLACK))
    assert "pin" in sig.motifs


def test_scholars_mate_detects_king_attack() -> None:
    board = chess.Board()
    for uci in ("e2e4", "e7e5", "d1h5", "b8c6", "f1c4"):
        board.push_uci(uci)
    losing = board.copy()
    move = chess.Move.from_uci("g8f6")
    board.push(move)
    loss = LossPoint(
        ply=5,
        board_before=losing,
        move=move,
        eval_before=0.0,
        eval_after=-1000.0,
        swing_against_loser=1000.0,
        loser_color=chess.BLACK,
    )
    sig = extract_signature(loss)
    assert "king_attack" in sig.motifs
    assert sig.severity == 1.0


def test_back_rank_detected() -> None:
    sig = extract_signature(_loss_point("6k1/5ppp/8/8/8/8/8/3R2K1 w - - 0 1", "d1d8", chess.BLACK))
    assert "back_rank" in sig.motifs
    assert "king_attack" in sig.motifs


def test_phase_boundaries() -> None:
    opening = extract_signature(_loss_point("3q1r1k/8/8/8/3N4/8/8/6K1 w - - 0 1", "d4e6", chess.BLACK))
    assert opening.phase == "opening"
    endgame = extract_signature(_loss_point("8/8/8/4k3/8/8/8/4K3 w - - 11 41", "e1e2", chess.WHITE))
    assert endgame.phase == "endgame"


def test_attack_pressure_clipped() -> None:
    sig = extract_signature(_loss_point("3q1r1k/8/8/8/3N4/8/8/6K1 w - - 0 1", "d4e6", chess.BLACK, swing=1600))
    assert sig.features["attack_pressure"] == 1.0
    assert sig.features["material_swing"] == 10.0
