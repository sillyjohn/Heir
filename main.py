import util 
from state import GameState
from rule import generatemoves
import alphabeta

INITIAL_BOARD = [
    list("gytsnxpnstyg"),
    list("bbbbbbbbbbbb"),
    list("............"),
    list("............"),
    list("............"),
    list("............"),
    list("............"),
    list("............"),
    list("............"),
    list("............"),
    list("BBBBBBBBBBBB"),
    list("GYTSNXPNSTYG"),
]

# Opening moves indexed by own turn number (0-based).
OPENING_BOOK = {
    0: [((10, 5), (8, 5)), ((10, 6), (8, 6)), ((10, 4), (8, 4))],  # White
    1: [((1, 5), (3, 5)), ((1, 6), (3, 6)), ((1, 4), (3, 4))],      # Black
}

def estimate_ply(board: list[list[str]]) -> int:
    diff = 0
    for r in range(12):
        for c in range(12):
            if board[r][c] != INITIAL_BOARD[r][c]:
                diff += 1
    # Typical move changes two squares; captures can change more.
    return diff // 2

def predefined_opening_move(state: GameState):
    legal_moves = set(generatemoves(state))
    if not legal_moves:
        return None

    ply = estimate_ply(state.board)
    own_turn_index = ply // 2
    if own_turn_index >= 5:
        return None

    for move in OPENING_BOOK[state.side]:
        if move in legal_moves:
            return move
    return None

def main():
    print("Welcome to Heir!")
    data = util.read_file()
    print(f"Own Side: {data.side}")
    print(f"Own Time: {data.ownTime}")
    print(f"Other Time: {data.otherTime}")
    for row in data.board:
        print("".join(row))
    print(f"Pieces: {data.pieces}")
    inferred_round = estimate_ply(data.board)
    state = GameState(data.board, data.pieces, inferred_round, 0 if data.side.upper() == "WHITE" else 1, None)
    depth = depthDecider(state, data)
    best_move = predefined_opening_move(state)
    if best_move is None:
        best_move = alphabeta.ab_minMax(state, depth)
    
    if best_move:
        util.write_output_move(best_move)
        print(f"Agent chose move: {best_move}")
    else:
        print("No valid moves found!")
def depthDecider(state: GameState, data: util.inputData):
    return 4
    
    return 3
if __name__ == "__main__":    
    main()
