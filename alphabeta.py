from state import GameState
import rule
import random
from evaluation import PIECES_VALUES, evaluation_function

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
OPENING_TURNS = 2

OPENING_BOOK = {
    # Per-ply candidate lists in priority order.
    0: [
        [((8, 5), (6, 5)), ((8, 6), (6, 6)), ((8, 4), (6, 4))],
        [((8, 6), (6, 6)), ((8, 5), (6, 5)), ((8, 7), (6, 7))],
        [((9, 5), (8, 5)), ((11, 6), (10, 6)), ((8, 4), (6, 4))],
        [((11, 6), (10, 6)), ((8, 4), (6, 4)), ((8, 7), (6, 7))],
        [((8, 4), (6, 4)), ((8, 7), (6, 7)), ((11, 3), (10, 3))],
    ],
    1: [
        [((1, 6), (3, 6)), ((1, 5), (3, 5)), ((1, 7), (3, 7))],
        [((1, 5), (3, 5)), ((1, 6), (3, 6)), ((1, 7), (3, 7))],
        [((0, 6), (1, 6)), ((1, 7), (3, 7)), ((2, 9), (4, 9))],
        [((1, 7), (3, 7)), ((2, 9), (4, 9)), ((1, 4), (3, 4))],
        [((2, 9), (4, 9)), ((1, 4), (3, 4)), ((0, 3), (1, 3))],
    ],
}

def applymove_inplace(board, pieces, move, side):
    src, dest = move
    src_r, src_c = src
    dest_r, dest_c = dest

    src_piece = board[src_r][src_c]
    dest_piece = board[dest_r][dest_c]

    pieces[src_piece].remove(src)
    pieces[src_piece].add(dest)
    if dest_piece != ".":
        pieces[dest_piece].remove(dest)

    board[src_r][src_c] = "."
    board[dest_r][dest_c] = src_piece

    winner = side if dest_piece in ("P", "p") else None
    return src_piece, dest_piece, winner

def undomove_inplace(board, pieces, move, src_piece, dest_piece):
    src, dest = move
    src_r, src_c = src
    dest_r, dest_c = dest

    pieces[src_piece].remove(dest)
    pieces[src_piece].add(src)
    if dest_piece != ".":
        pieces[dest_piece].add(dest)

    board[src_r][src_c] = src_piece
    board[dest_r][dest_c] = dest_piece

def move_sort_key(state: GameState, move):
    board = state.board
    (src_r, src_c), (dest_r, dest_c) = move
    src_piece = board[src_r][src_c]
    dest_piece = board[dest_r][dest_c]

    capture_score = 0
    if dest_piece == "P" or dest_piece == "p":
        capture_score = 10_000_000
    elif dest_piece != ".":
        capture_score = PIECES_VALUES[dest_piece.upper()]

    mover_priority = PIECES_MOVEMENT_PRIORITY.get(src_piece.upper(), 99)
    center_distance = abs(dest_r - 5.5) + abs(dest_c - 5.5)
    return (capture_score, -mover_priority, -center_distance)

def order_moves(state: GameState, moves):
    return sorted(moves, key=lambda mv: move_sort_key(state, mv), reverse=True)

def is_opening_candidate_legal(state: GameState, move, source_cache=None):
    """Validate one opening candidate using only its source piece move function."""
    (src_r, src_c), (dest_r, dest_c) = move
    if not (0 <= src_r < BOARD_SIZE and 0 <= src_c < BOARD_SIZE):
        return False
    if not (0 <= dest_r < BOARD_SIZE and 0 <= dest_c < BOARD_SIZE):
        return False

    board = state.board
    src_piece = board[src_r][src_c]
    if src_piece == ".":
        return False
    if state.side == 0 and not src_piece.isupper():
        return False
    if state.side == 1 and not src_piece.islower():
        return False

    move_fn = rule.move_functions.get(src_piece.upper())
    if move_fn is None:
        return False

    src = (src_r, src_c)
    generated_moves = source_cache.get(src) if source_cache is not None else None
    if generated_moves is None:
        moves_from_src = []
        move_fn(board, state.side, src, moves_from_src)
        generated_moves = set(moves_from_src)
        if source_cache is not None:
            source_cache[src] = generated_moves

    return move in generated_moves

def select_predefined_opening_move(gameState: GameState, move_count: int):
    if move_count < 0 or move_count >= OPENING_TURNS:
        return None

    book_by_side = OPENING_BOOK.get(gameState.side)
    if not book_by_side:
        return None
    if move_count >= len(book_by_side):
        return None

    candidates = book_by_side[move_count]
    if not candidates:
        return None

    source_cache = {}
    legal_candidates = []
    for move in candidates:
        if is_opening_candidate_legal(gameState, move, source_cache):
            legal_candidates.append(move)

    if legal_candidates:
        return random.choice(legal_candidates)

    # No legal opening candidates for this ply; fall back to alpha-beta in main.
    return None

def ab_minMax(gameState: GameState, depth):
    best_move = None
    best_moves = []
    alpha = float('-inf')
    beta = float('inf')
    board = gameState.board
    pieces = gameState.pieces
    winner = gameState.winner
    
    # Generate the initial moves for the root state
    moves = order_moves(gameState, rule.generatemoves(gameState))
    if not moves:
        return None  # No moves available 

    if gameState.side == 0:  # Maximize white
        best_score = float('-inf')
        for move in moves:
            src_piece, dest_piece, new_winner = applymove_inplace(board, pieces, move, gameState.side)
            child_winner = winner if winner is not None else new_winner
            score = minVal(
                board,
                pieces,
                gameState.round + 1,
                1,
                child_winner,
                depth - 1,
                alpha,
                beta,
                move,
            )
            undomove_inplace(board, pieces, move, src_piece, dest_piece)
            
            # If we found a strictly better score,
            # update best_score AND save the move
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
                
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
        best_move = random.choice(best_moves) if best_moves else moves[0]
        print(f"best move for white: {best_move}, score: {best_score}, piece: {gameState.board[best_move[0][0]][best_move[0][1]]}")
        return best_move

    else:  # Minimize black
        best_score = float('inf')
        for move in moves:
            src_piece, dest_piece, new_winner = applymove_inplace(board, pieces, move, gameState.side)
            child_winner = winner if winner is not None else new_winner
            score = maxVal(
                board,
                pieces,
                gameState.round + 1,
                0,
                child_winner,
                depth - 1,
                alpha,
                beta,
                move,
            )
            undomove_inplace(board, pieces, move, src_piece, dest_piece)
            
            # If we found a strictly better (lower) score, update best_score AND save the move
            if score < best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
                
            beta = min(beta, best_score)
            if alpha >= beta:
                break
        best_move = random.choice(best_moves) if best_moves else moves[0]
        print(f"best move for black: {best_move}, score: {best_score}, piece: {gameState.board[best_move[0][0]][best_move[0][1]]}")
        return best_move

def maxVal(board, pieces, round_num, side, winner, depth, alpha, beta, last_move=None):
    best = float('-inf')
    if winner is not None:
        if winner == 0:
            return float('inf')
        else:
            return float('-inf')

    state = GameState(board, pieces, round_num, side, winner)
    if depth <= 0:
        return evaluation_function(state, last_move)

    moves = order_moves(state, rule.generatemoves(state))
    if not moves:
        return evaluation_function(state, last_move)

    # Iterate through all moves, then compare the best value with move's best value
    for move in moves:
        src_piece, dest_piece, new_winner = applymove_inplace(board, pieces, move, side)
        child_winner = winner if winner is not None else new_winner
        best = max(
            best,
            minVal(board, pieces, round_num + 1, 1 - side, child_winner, depth - 1, alpha, beta, move),
        )
        undomove_inplace(board, pieces, move, src_piece, dest_piece)
        if best >= beta:
            return best
        alpha = max(best,alpha)
    return best

def minVal(board, pieces, round_num, side, winner, depth, alpha, beta, last_move=None):
    worst = float('inf')
    if winner is not None:
        if winner == 0:
            return float('inf')
        else:
            return float('-inf')

    state = GameState(board, pieces, round_num, side, winner)
    if depth <= 0:
        return evaluation_function(state, last_move)
    moves = order_moves(state, rule.generatemoves(state))
    if not moves:
        return evaluation_function(state, last_move) 

    # Iterate through all moves, then compare the best value with move's best value
    for move in moves:
        src_piece, dest_piece, new_winner = applymove_inplace(board, pieces, move, side)
        child_winner = winner if winner is not None else new_winner
        worst = min(
            worst,
            maxVal(board, pieces, round_num + 1, 1 - side, child_winner, depth - 1, alpha, beta, move),
        )
        undomove_inplace(board, pieces, move, src_piece, dest_piece)
        if worst <= alpha:
            return worst
        beta = min(worst,beta)
    return worst
    
