import util 
from state import GameState
from rule import generatemoves
import alphabeta

def main():
    print("Welcome to Heir!")
    data = util.read_file()
    print(f"Own Side: {data.side}")
    print(f"Own Time: {data.ownTime}")
    print(f"Other Time: {data.otherTime}")
    for row in data.board:
        print("".join(row))
    print(f"Pieces: {data.pieces}")
    state = GameState(data.board,data.pieces, 0, 0 if data.side.upper() == "WHITE" else 1, None)
    depth = depthDecider(state, data)
    # Call your root function with a depth (e.g., Depth 3)
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
