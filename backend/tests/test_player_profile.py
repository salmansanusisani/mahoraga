from app.profiling.player_profile import apply_opening_strength_signal
from app.models.db_models import Player


def test_clean_opening_move_raises_strength() -> None:
    player = Player(estimated_strength=800)
    assert apply_opening_strength_signal(player, 20)
    assert player.estimated_strength == 825


def test_bad_opening_move_does_not_raise_strength() -> None:
    player = Player(estimated_strength=800)
    assert not apply_opening_strength_signal(player, 50)
    assert player.estimated_strength == 800
