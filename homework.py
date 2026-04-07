import util 
from state import GameState
import alphabeta


def parse_time_to_int(value: str) -> int:
    try:
        return int(float(value.strip()))
    except (ValueError, AttributeError):
        return 0


def parse_round_to_int() -> int:
    return util.get_round_count()

def main():
    data = util.read_file()
    state = GameState(data.board,data.pieces, 0, 0 if data.side.upper() == "WHITE" else 1, None)
    move_count = parse_round_to_int()
    position_counts = util.load_position_counts()
    if move_count == 0:
        util.clear_position_counts()
        position_counts.clear()

    root_key = alphabeta.compute_zobrist_hash(state.board, state.side)
    util.increment_position_count(position_counts, root_key)

    best_move = alphabeta.select_predefined_opening_move(
        state,
        move_count,
        position_counts=position_counts,
        root_key=root_key,
    )
    if best_move is None:
        depth = depthDecider(data, move_count)
        # Call your root function with a depth (e.g., Depth 3)
        best_move = alphabeta.ab_minMax(state, depth, position_counts=position_counts)
    
    if best_move:
        child_key = alphabeta.next_position_key_from_move(root_key, state.board, best_move)
        util.increment_position_count(position_counts, child_key)
        util.save_position_counts(position_counts)
        util.countRound()
        util.write_output_move(best_move)
    else:
        print("No valid moves found!")
def count_pieces_on_board(board) -> int:
    return sum(1 for row in board for cell in row if cell != ".")


def depthDecider(data: util.inputData, move_count: int):
    own_time = parse_time_to_int(data.ownTime)
    opp_time = parse_time_to_int(data.otherTime)
    # Initial setup has 48 pieces total (24 per side). Missing pieces are captures.
    piece_count = count_pieces_on_board(data.board)
    captures_so_far = max(0, 48 - piece_count)

    # Early if captures are still low (requested rule) or by low move count heuristic.
    is_early = captures_so_far < 3 or move_count < 18
    is_mid = captures_so_far < 12 or move_count < 55

    if is_early:
        depth = 2
    elif is_mid:
        depth = 3
    else:
        # Deepen in cleaner endgames.
        depth = 4 if piece_count <= 20 else 3

    # Time-pressure controls.
    if own_time < 20:
        depth = min(depth, 2)
    elif own_time < 60:
        depth = min(depth, 3)
    elif own_time > 180 and own_time > opp_time + 30:
        depth += 1

    return max(2, min(5, depth))
if __name__ == "__main__":    
    main()
