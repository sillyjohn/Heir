import util 
from state import GameState
from rule import generatemoves
import alphabeta


def parse_time_to_int(value: str) -> int:
    try:
        return int(float(value.strip()))
    except (ValueError, AttributeError):
        return 0


def parse_round_to_int() -> int:
    try:
        with open("playdata.txt", "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def main():
    data = util.read_file()
    state = GameState(data.board,data.pieces, 0, 0 if data.side.upper() == "WHITE" else 1, None)
    depth = depthDecider(state, data)
    # Call your root function with a depth (e.g., Depth 3)
    best_move = alphabeta.ab_minMax(state, depth)
    
    if best_move:
        util.countRound()
        util.write_output_move(best_move)
    else:
        print("No valid moves found!")
def depthDecider(state: GameState, data: util.inputData):
    own_time = parse_time_to_int(data.ownTime)
    move_count = parse_round_to_int()
    # Early game: <10 moves
    if move_count < 10:
        return 2
    # Mid game: 10-59 moves (boundary 10 treated as mid)
    if move_count < 60:
        if own_time > 200:
            return 4
        return 3
    # Late game: >=60 moves (boundary 60 treated as late)
    if own_time > 150:
        return 4
    if own_time > 50:
        return 3
    return 2
if __name__ == "__main__":    
    main()
