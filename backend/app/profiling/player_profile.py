"""Small, transparent player-style model built from completed games."""
from __future__ import annotations

import chess

from app.models.db_models import Game, Player


def update_profile(player: Player, game: Game) -> None:
    board = chess.Board()
    white_moves = 0
    captures = 0
    sacrifices = 0
    early_center = 0
    for index, uci in enumerate(game.moves):
        move = chess.Move.from_uci(uci)
        piece = board.piece_at(move.from_square)
        captured = board.piece_at(move.to_square)
        if index % 2 == 0:
            white_moves += 1
            if board.is_capture(move):
                captures += 1
            if piece and captured and piece.piece_type in (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN) and captured.piece_type == chess.PAWN:
                sacrifices += 1
            if white_moves <= 5 and move.to_square in (chess.D4, chess.E4, chess.D5, chess.E5):
                early_center += 1
        board.push(move)
    games = max(1, player.games_played)
    current = player.style_vector or {}
    observed = {
        "tactical_aggression": min(1.0, captures / max(1, white_moves)),
        "risk_tolerance": min(1.0, sacrifices / max(1, white_moves)),
        "opening_preparation": min(1.0, early_center / 2),
        "endgame_strength": 1.0 if board.fullmove_number >= 35 and game.result == "1-0" else 0.0,
        "king_attack_frequency": min(1.0, captures / max(1, white_moves * 0.6)),
    }
    player.style_vector = {
        name: round((current.get(name, observed[name]) * (games - 1) + value) / games, 3)
        for name, value in observed.items()
    }


def apply_opening_strength_signal(player: Player, centipawn_loss: float) -> bool:
    """Raise only the strength floor when an early player move is engine-clean."""
    if centipawn_loss > 35 or player.estimated_strength >= 2400:
        return False
    player.estimated_strength = min(2400, player.estimated_strength + 25)
    return True
