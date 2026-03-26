from state import GameState
import rule
import copy 
import random
from rule import countMoves  # Add this import

PIECES_VALUES= {
    "B":100,
    "P":2000,
    "X":700,
    "Y":600,
    "G":200,
    "T":400,
    "S":700,
    "N":300,
}

PIECES_MOVEMENT_PRIORITY = {
    "P": 1,
    "X": 2,
    "Y": 3,
    "S": 4,
    "G": 5,
    "T": 6, 
    "N": 7,
    "B": 8
}

BOARD_SIZE = 12
MAX_L1_DISTANCE = (BOARD_SIZE - 1) * 2
DISTANCE_WEIGHT = 0.1
CAPTURE_WEIGHT = 0.3
OPEN_MOVE_WEIGHT = 0.2



def evaluation_function(gameState, last_move=None):
    # Calculate the score of the game state
    # For now, just add up all the pieces on the board, 
    # with positive values for white and negative values for black
    board = gameState.board
    score = 0
    move_count = countMoves(gameState)  # Get the number of moves available to the current player
    #reward move that open up more moves for the agent, and penalize move that reduce the agent's mobility. This is to encourage the agent to make moves that increase its options in future turns.
    if gameState.side == 0:
        score += move_count * OPEN_MOVE_WEIGHT
    else:
        score -= move_count * OPEN_MOVE_WEIGHT

    for i in range(12):
        for j in range(12):
            piece = board[i][j]
            if piece == ".":
                continue
            value = PIECES_VALUES[piece.upper()]
            if piece.isupper():
                score += value
            elif piece.islower():
                score -= value

    # Optional heuristic: reward the last moved piece if it is closer to the opponent prince.
    if last_move is not None:
        _, dest = last_move
        dest_r, dest_c = dest
        moved_piece = board[dest_r][dest_c]
        if moved_piece != ".":
            if moved_piece.isupper():
                opponent_prince_positions = gameState.pieces.get("p")
                if opponent_prince_positions:
                    prince_r, prince_c = next(iter(opponent_prince_positions))
                    dist = abs(dest_r - prince_r) + abs(dest_c - prince_c)
                    score += DISTANCE_WEIGHT * (MAX_L1_DISTANCE - dist)
            else:
                opponent_prince_positions = gameState.pieces.get("P")
                if opponent_prince_positions:
                    prince_r, prince_c = next(iter(opponent_prince_positions))
                    dist = abs(dest_r - prince_r) + abs(dest_c - prince_c)
                    score -= DISTANCE_WEIGHT * (MAX_L1_DISTANCE - dist)
    # if the move, base on their movement rule, can get closer to some pieces in the next time,
    # reward them base of what they can capture potentially in the next move. This is to encourage the agent to make moves that set up future captures.
    if last_move is not None:
        _, dest = last_move
        dest_r, dest_c = dest
        moved_piece = board[dest_r][dest_c]
        if moved_piece.isupper():
            side =0
        else:
            side =1
        if moved_piece != ".":
            potential_moves = []
            if moved_piece.upper() in rule.move_functions:
                rule.move_functions[moved_piece.upper()](board, side, (dest_r, dest_c), potential_moves)
            capture_value = 0
            for potential_move in potential_moves:
                _, potential_dest = potential_move
                potential_dest_r, potential_dest_c = potential_dest
                target_piece = board[potential_dest_r][potential_dest_c]
                if side == 0 and target_piece.islower():
                    capture_value = max(capture_value, PIECES_VALUES[target_piece.upper()])
                elif side == 1 and target_piece.isupper():
                    capture_value = min(capture_value, -PIECES_VALUES[target_piece.upper()])
            score += CAPTURE_WEIGHT * capture_value
    return score

def updatedState(state: GameState, move):
    # Update state
    new_Round =state.round + 1
    # apply move
    new_board,new_pieces,new_winner = applymove(state,move)
    # flip side
    new_side = 1 - state.side

    return GameState(new_board,new_pieces,new_Round,new_side,new_winner)

def applymove(state: GameState, move):
    # Prep for deep copy and data access
    board = state.board
    new_board = copy.deepcopy(board)
    pieces = state.pieces
    new_pieces = copy.deepcopy(pieces)

    # Parse move
    src,dest = move
    src_r,src_c = src
    dest_r, dest_c = dest
    winner = None

    # Get the moving pieces and destination piece's info
    src_piece = board[src_r][src_c]
    dest_piece = board[dest_r][dest_c]
    # Winner checking
    if dest_piece == "P" or dest_piece == "p":
        winner = state.side

    # update the src piece's location in both board and pieces
    new_pieces[src_piece].remove(src)
    new_pieces[src_piece].add(dest)
    new_board[src_r][src_c] = "." 
    new_board[dest_r][dest_c] = src_piece

    # handle destination pieces
    if dest_piece != ".": # if the destination is not empty
        new_pieces[dest_piece].remove(dest)

    return new_board,new_pieces,winner

def ab_minMax(gameState: GameState, depth):
    best_move = None
    best_moves = []
    alpha = float('-inf')
    beta = float('inf')
    
    # Generate the initial moves for the root state
    moves = rule.generatemoves(gameState)
    if not moves:
        return None  # No moves available 

    if gameState.side == 0:  # Maximize white
        best_score = float('-inf')
        for move in moves:
            new_state = updatedState(gameState, move)
            # Call minVal because it will be Black's turn next
            score = minVal(new_state, depth - 1, alpha, beta, move)
            
            # If we found a strictly better score,
            # update best_score AND save the move
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
                
            alpha = max(alpha, best_score)
        best_move = random.choice(best_moves) if best_moves else moves[0]
        print(f"best move for white: {best_move}, score: {best_score}, piece: {gameState.board[best_move[0][0]][best_move[0][1]]}")
        return best_move

    else:  # Minimize black
        best_score = float('inf')
        for move in moves:
            new_state = updatedState(gameState, move)
            # Call maxVal because it will be White's turn next
            score = maxVal(new_state, depth - 1, alpha, beta, move)
            
            # If we found a strictly better (lower) score, update best_score AND save the move
            if score < best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
                
            beta = min(beta, best_score)
        best_move = random.choice(best_moves) if best_moves else moves[0]
        print(f"best move for black: {best_move}, score: {best_score}, piece: {gameState.board[best_move[0][0]][best_move[0][1]]}")
        return best_move

def maxVal(state, depth ,alpha, beta, last_move=None):
    best = float('-inf')
    if state.winner is not None:
        if state.winner == 0:
            return float('inf')
        else:
            return float('-inf')
    if depth <= 0:
        return evaluation_function(state, last_move)

    moves = rule.generatemoves(state)
    if not moves:
        return evaluation_function(state, last_move)

    # Iterate through all moves, then compare the best value with move's best value
    for move in moves:
        new_state = updatedState(state,move)
        best = max(best,minVal(new_state,depth-1,alpha,beta,move))
        if best >= beta:
            return best
        alpha = max(best,alpha)
    return best

def minVal(state, depth ,alpha, beta, last_move=None):
    worst = float('inf')
    if state.winner is not None:
        if state.winner == 0:
            return float('inf')
        else:
            return float('-inf')

    if depth <= 0:
        return evaluation_function(state, last_move)
    moves = rule.generatemoves(state)
    if not moves:
        return evaluation_function(state, last_move) 

    # Iterate through all moves, then compare the best value with move's best value
    for move in moves:
        new_state = updatedState(state,move)
        worst = min(worst,maxVal(new_state,depth-1,alpha,beta,move))
        if worst <= alpha:
            return worst
        beta = min(worst,beta)
    return worst
    
