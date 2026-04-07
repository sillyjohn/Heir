from state import GameState
from dataclasses import dataclass
from typing import Optional
import rule
import random
from evaluation import PIECES_VALUES, evaluation_function

PIECES_MOVEMENT_PRIORITY = {
    "P": 1,
    "X": 2,
    "Y": 6,
    "S": 3,
    "G": 5,
    "T": 4, 
    "N": 7,
    "B": 8
}

BOARD_SIZE = 12
OPENING_TURNS = 2
THREEFOLD_COUNT = 3

TT_EXACT = "EXACT"
TT_LOWER = "LOWER"
TT_UPPER = "UPPER"
TT_FLAG_STRENGTH = {TT_UPPER: 1, TT_LOWER: 1, TT_EXACT: 2}
TT_DEBUG = False

PIECE_SYMBOLS = tuple(PIECES_VALUES.keys()) + tuple(piece.lower() for piece in PIECES_VALUES.keys())
PIECE_TO_INDEX = {piece: idx for idx, piece in enumerate(PIECE_SYMBOLS)}
_ZOBRIST_RNG = random.Random(561)
ZOBRIST_TABLE = [
    [[_ZOBRIST_RNG.getrandbits(64) for _ in PIECE_SYMBOLS] for _ in range(BOARD_SIZE)]
    for _ in range(BOARD_SIZE)
]
ZOBRIST_SIDE_KEY = _ZOBRIST_RNG.getrandbits(64)

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

@dataclass
class TTEntry:
    depth: int
    score: float
    flag: str
    best_move: Optional[tuple] = None

def compute_zobrist_hash(board, side):
    pos_key = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r][c]
            if piece != ".":
                pos_key ^= ZOBRIST_TABLE[r][c][PIECE_TO_INDEX[piece]]
    if side == 1:
        pos_key ^= ZOBRIST_SIDE_KEY
    return pos_key

def update_zobrist_hash(pos_key, move, src_piece, dest_piece):
    (src_r, src_c), (dest_r, dest_c) = move

    pos_key ^= ZOBRIST_TABLE[src_r][src_c][PIECE_TO_INDEX[src_piece]]
    if dest_piece != ".":
        pos_key ^= ZOBRIST_TABLE[dest_r][dest_c][PIECE_TO_INDEX[dest_piece]]
    pos_key ^= ZOBRIST_TABLE[dest_r][dest_c][PIECE_TO_INDEX[src_piece]]
    pos_key ^= ZOBRIST_SIDE_KEY
    return pos_key


def next_position_key_from_move(pos_key, board, move):
    (src_r, src_c), (dest_r, dest_c) = move
    src_piece = board[src_r][src_c]
    dest_piece = board[dest_r][dest_c]
    return update_zobrist_hash(pos_key, move, src_piece, dest_piece)


def is_threefold_repetition_key(position_counts, pos_key):
    if not position_counts:
        return False
    return position_counts.get(pos_key, 0) >= (THREEFOLD_COUNT - 1)


def partition_repetition_safe_moves(board, moves, root_key, position_counts):
    if not position_counts:
        return moves, []

    safe_moves = []
    repeat_moves = []
    for move in moves:
        child_key = next_position_key_from_move(root_key, board, move)
        if is_threefold_repetition_key(position_counts, child_key):
            repeat_moves.append(move)
        else:
            safe_moves.append(move)
    return safe_moves, repeat_moves

def should_replace_tt_entry(existing_entry, new_depth, new_flag):
    if existing_entry is None:
        return True
    if new_depth > existing_entry.depth:
        return True
    if new_depth < existing_entry.depth:
        return False
    return TT_FLAG_STRENGTH[new_flag] > TT_FLAG_STRENGTH[existing_entry.flag]

def apply_tt_move_ordering(moves, tt_entry):
    if tt_entry is None or tt_entry.best_move is None:
        return
    for idx, move in enumerate(moves):
        if move == tt_entry.best_move:
            if idx != 0:
                moves[0], moves[idx] = moves[idx], moves[0]
            return

def maybe_store_tt(tt, pos_key, depth, score, flag, best_move):
    existing = tt.get(pos_key)
    if should_replace_tt_entry(existing, depth, flag):
        tt[pos_key] = TTEntry(depth=depth, score=score, flag=flag, best_move=best_move)

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

def select_predefined_opening_move(
    gameState: GameState,
    move_count: int,
    position_counts=None,
    root_key=None,
):
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
        if root_key is None:
            root_key = compute_zobrist_hash(gameState.board, gameState.side)
        non_repeat_candidates = []
        for move in legal_candidates:
            child_key = next_position_key_from_move(root_key, gameState.board, move)
            if not is_threefold_repetition_key(position_counts, child_key):
                non_repeat_candidates.append(move)
        if non_repeat_candidates:
            return random.choice(non_repeat_candidates)
        return random.choice(legal_candidates)

    # No legal opening candidates for this ply; fall back to alpha-beta in main.
    return None

def ab_minMax(gameState: GameState, depth, position_counts=None):
    best_move = None
    best_moves = []
    alpha = float('-inf')
    beta = float('inf')
    board = gameState.board
    pieces = gameState.pieces
    winner = gameState.winner
    root_key = compute_zobrist_hash(board, gameState.side)
    tt = {}
    search_stats = {"nodes": 0, "tt_probes": 0, "tt_hits": 0, "tt_cutoffs": 0}
    
    # Generate the initial moves for the root state
    moves = order_moves(gameState, rule.generatemoves(gameState))
    if not moves:
        return None  # No moves available 

    safe_moves, repeat_moves = partition_repetition_safe_moves(
        board,
        moves,
        root_key,
        position_counts,
    )
    if safe_moves:
        moves = safe_moves
        if TT_DEBUG and repeat_moves:
            print(f"repetition filter avoided {len(repeat_moves)} move(s) at root")

    if gameState.side == 0:  # Maximize white
        best_score = float('-inf')
        for move in moves:
            src_piece, dest_piece, new_winner = applymove_inplace(board, pieces, move, gameState.side)
            child_winner = winner if winner is not None else new_winner
            child_key = update_zobrist_hash(root_key, move, src_piece, dest_piece)
            score = minVal(
                board,
                pieces,
                gameState.round + 1,
                1,
                child_winner,
                depth - 1,
                alpha,
                beta,
                child_key,
                tt,
                search_stats,
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
        best_move = best_moves[0] if best_moves else moves[0]
        print(f"best move for white: {best_move}, score: {best_score}, piece: {gameState.board[best_move[0][0]][best_move[0][1]]}")
        if TT_DEBUG:
            print(
                f"tt stats | nodes={search_stats['nodes']} probes={search_stats['tt_probes']} "
                f"hits={search_stats['tt_hits']} cutoffs={search_stats['tt_cutoffs']} size={len(tt)}"
            )
        return best_move

    else:  # Minimize black
        best_score = float('inf')
        for move in moves:
            src_piece, dest_piece, new_winner = applymove_inplace(board, pieces, move, gameState.side)
            child_winner = winner if winner is not None else new_winner
            child_key = update_zobrist_hash(root_key, move, src_piece, dest_piece)
            score = maxVal(
                board,
                pieces,
                gameState.round + 1,
                0,
                child_winner,
                depth - 1,
                alpha,
                beta,
                child_key,
                tt,
                search_stats,
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
        best_move = best_moves[0] if best_moves else moves[0]
        print(f"best move for black: {best_move}, score: {best_score}, piece: {gameState.board[best_move[0][0]][best_move[0][1]]}")
        if TT_DEBUG:
            print(
                f"tt stats | nodes={search_stats['nodes']} probes={search_stats['tt_probes']} "
                f"hits={search_stats['tt_hits']} cutoffs={search_stats['tt_cutoffs']} size={len(tt)}"
            )
        return best_move

def maxVal(board, pieces, round_num, side, winner, depth, alpha, beta, pos_key, tt, search_stats, last_move=None):
    search_stats["nodes"] += 1
    best = float('-inf')
    if winner is not None:
        if winner == 0:
            return float('inf')
        else:
            return float('-inf')

    # Keep TT strictly for internal nodes where value is position-dependent.
    if depth <= 0:
        state = GameState(board, pieces, round_num, side, winner)
        return evaluation_function(state, last_move)

    alpha_orig = alpha
    beta_orig = beta
    tt_entry = None
    search_stats["tt_probes"] += 1
    tt_entry = tt.get(pos_key)
    if tt_entry is not None and tt_entry.depth >= depth:
        search_stats["tt_hits"] += 1
        if tt_entry.flag == TT_EXACT:
            return tt_entry.score
        if tt_entry.flag == TT_LOWER:
            alpha = max(alpha, tt_entry.score)
        elif tt_entry.flag == TT_UPPER:
            beta = min(beta, tt_entry.score)
        if alpha >= beta:
            search_stats["tt_cutoffs"] += 1
            return tt_entry.score

    state = GameState(board, pieces, round_num, side, winner)
    moves = order_moves(state, rule.generatemoves(state))
    if not moves:
        return evaluation_function(state, last_move)
    apply_tt_move_ordering(moves, tt_entry)

    # Iterate through all moves, then compare the best value with move's best value
    best_move = None
    for move in moves:
        src_piece, dest_piece, new_winner = applymove_inplace(board, pieces, move, side)
        child_winner = winner if winner is not None else new_winner
        child_key = update_zobrist_hash(pos_key, move, src_piece, dest_piece)
        score = minVal(
            board,
            pieces,
            round_num + 1,
            1 - side,
            child_winner,
            depth - 1,
            alpha,
            beta,
            child_key,
            tt,
            search_stats,
            move,
        )
        if score > best:
            best = score
            best_move = move

        undomove_inplace(board, pieces, move, src_piece, dest_piece)
        if best >= beta:
            break
        alpha = max(best,alpha)

    if best <= alpha_orig:
        flag = TT_UPPER
    elif best >= beta_orig:
        flag = TT_LOWER
    else:
        flag = TT_EXACT
    maybe_store_tt(tt, pos_key, depth, best, flag, best_move)
    return best

def minVal(board, pieces, round_num, side, winner, depth, alpha, beta, pos_key, tt, search_stats, last_move=None):
    search_stats["nodes"] += 1
    worst = float('inf')
    if winner is not None:
        if winner == 0:
            return float('inf')
        else:
            return float('-inf')

    # Keep TT strictly for internal nodes where value is position-dependent.
    if depth <= 0:
        state = GameState(board, pieces, round_num, side, winner)
        return evaluation_function(state, last_move)

    alpha_orig = alpha
    beta_orig = beta
    tt_entry = None
    search_stats["tt_probes"] += 1
    tt_entry = tt.get(pos_key)
    if tt_entry is not None and tt_entry.depth >= depth:
        search_stats["tt_hits"] += 1
        if tt_entry.flag == TT_EXACT:
            return tt_entry.score
        if tt_entry.flag == TT_LOWER:
            alpha = max(alpha, tt_entry.score)
        elif tt_entry.flag == TT_UPPER:
            beta = min(beta, tt_entry.score)
        if alpha >= beta:
            search_stats["tt_cutoffs"] += 1
            return tt_entry.score

    state = GameState(board, pieces, round_num, side, winner)
    moves = order_moves(state, rule.generatemoves(state))
    if not moves:
        return evaluation_function(state, last_move)
    apply_tt_move_ordering(moves, tt_entry)

    # Iterate through all moves, then compare the best value with move's best value
    best_move = None
    for move in moves:
        src_piece, dest_piece, new_winner = applymove_inplace(board, pieces, move, side)
        child_winner = winner if winner is not None else new_winner
        child_key = update_zobrist_hash(pos_key, move, src_piece, dest_piece)
        score = maxVal(
            board,
            pieces,
            round_num + 1,
            1 - side,
            child_winner,
            depth - 1,
            alpha,
            beta,
            child_key,
            tt,
            search_stats,
            move,
        )
        if score < worst:
            worst = score
            best_move = move

        undomove_inplace(board, pieces, move, src_piece, dest_piece)
        if worst <= alpha:
            break
        beta = min(worst,beta)

    if worst <= alpha_orig:
        flag = TT_UPPER
    elif worst >= beta_orig:
        flag = TT_LOWER
    else:
        flag = TT_EXACT
    maybe_store_tt(tt, pos_key, depth, worst, flag, best_move)
    return worst
    
