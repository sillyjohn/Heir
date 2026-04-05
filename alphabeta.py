from state import GameState
import rule
import copy 

PIECES_VALUES= {
    "B":100,
    "P":800,
    "X":700,
    "Y":600,
    "G":200,
    "T":400,
    "S":300,
    "N":500,
}

WIN_SCORE = 10_000_000

def evaluation_function(gameState):
    # Calculate the score of the game state
    # For now, just add up all the pieces on the board, 
    # with positive values for white and negative values for black
    board = gameState.board
    score = 0
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
    return score

def order_moves(state: GameState, moves):
    board = state.board
    side = state.side

    def score_move(move):
        _, dest = move
        dest_r, dest_c = dest
        captured = board[dest_r][dest_c]
        if captured == ".":
            return 0
        value = PIECES_VALUES[captured.upper()]
        return value if side == 0 else -value

    return sorted(moves, key=score_move, reverse=True)

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
    alpha = float('-inf')
    beta = float('inf')
    
    # Generate the initial moves for the root state
    moves = order_moves(gameState, rule.generatemoves(gameState))
    if not moves:
        return None  # No moves available 

    if gameState.side == 0:  # Maximize white
        best_score = float('-inf')
        for move in moves:
            new_state = updatedState(gameState, move)
            # Call minVal because it will be Black's turn next
            score = minVal(new_state, depth - 1, alpha, beta)
            
            # If we found a strictly better score,
            # update best_score AND save the move
            if score > best_score:
                best_score = score
                best_move = move
                
            alpha = max(alpha, best_score)
        return best_move

    else:  # Minimize black
        best_score = float('inf')
        for move in moves:
            new_state = updatedState(gameState, move)
            # Call maxVal because it will be White's turn next
            score = maxVal(new_state, depth - 1, alpha, beta)
            
            # If we found a strictly better (lower) score, update best_score AND save the move
            if score < best_score:
                best_score = score
                best_move = move
                
            beta = min(beta, best_score)
        return best_move

def maxVal(state, depth ,alpha, beta):
    best = float('-inf')
    if state.winner is not None:
        if state.winner == 0:
            return WIN_SCORE
        else:
            return -WIN_SCORE
    if depth <= 0:
        return evaluation_function(state)

    moves = order_moves(state, rule.generatemoves(state))
    if not moves:
        return evaluation_function(state)

    # Iterate through all moves, then compare the best value with move's best value
    for move in moves:
        new_state = updatedState(state,move)
        best = max(best,minVal(new_state,depth-1,alpha,beta))
        if best >= beta:
            return best
        alpha = max(best,alpha)
    return best

def minVal(state, depth ,alpha, beta):
    worst = float('inf')
    if state.winner is not None:
        if state.winner == 0:
            return WIN_SCORE
        else:
            return -WIN_SCORE

    if depth <= 0:
        return evaluation_function(state)
    moves = order_moves(state, rule.generatemoves(state))
    if not moves:
        return evaluation_function(state) 

    # Iterate through all moves, then compare the best value with move's best value
    for move in moves:
        new_state = updatedState(state,move)
        worst = min(worst,maxVal(new_state,depth-1,alpha,beta))
        if worst <= alpha:
            return worst
        beta = min(worst,beta)
    return worst
    
