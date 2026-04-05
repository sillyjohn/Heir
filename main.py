import util 
from state import GameState
import alphabeta
import rule


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
    move_count = parse_round_to_int()
    best_move = alphabeta.select_predefined_opening_move(state, move_count)
    if best_move is None:
        depth = depthDecider(data, state, move_count)
        # Call your root function with a depth (e.g., Depth 3)
        best_move = alphabeta.ab_minMax(state, depth)
    
    if best_move:
        util.countRound()
        util.write_output_move(best_move)
    else:
        print("No valid moves found!")
def depthDecider(data: util.inputData, state: GameState, move_count: int):
    own_time = parse_time_to_int(data.ownTime)
    opp_time = parse_time_to_int(data.otherTime)

    legal_moves = len(rule.generatemoves(state))
    non_prince_pieces = sum(
        len(locs) for piece, locs in data.pieces.items() if piece.upper() != "P"
    )

    # Base depth by game phase from remaining material.
    if non_prince_pieces > 22:
        depth = 2
    elif non_prince_pieces > 12:
        depth = 3
    else:
        depth = 4

    # Adjust for branching factor.
    if legal_moves >= 45:
        depth -= 1
    elif legal_moves <= 18:
        depth += 1

    # Time-pressure controls.
    if own_time < 20:
        depth = min(depth, 2)
    elif own_time < 60:
        depth = min(depth, 3)
    elif own_time > 180 and own_time > opp_time + 30:
        depth += 1

    # Keep search depth in a safe range.
    return max(2, min(5, depth))
if __name__ == "__main__":    
    main()
