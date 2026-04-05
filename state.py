from dataclasses import dataclass
from typing import List, Dict, Set, Tuple


@dataclass(frozen=True)
class GameState:
    board: List[List[str]]
    pieces: Dict[str, Set[Tuple[int, int]]]
    round: int
    side: int # 0 for white, 1 for black
    winner: int # 0 for white, 1 for black, -1 for draw, None for ongoing
    
