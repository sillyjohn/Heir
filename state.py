from dataclasses import dataclass

@dataclass(frozen=True)
class GameState:
    board: list[list[str]]
    pieces: dict[str, set[tuple[int, int]]]
    round: int
    side: int # 0 for white, 1 for black
    winner: int # 0 for white, 1 for black, -1 for draw, None for ongoing
    
