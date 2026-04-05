from state import GameState
import rule

PIECES_VALUES = {
    "B": 100,
    "P": 2000,
    "X": 700,
    "Y": 600,
    "G": 200,
    "T": 400,
    "S": 700,
    "N": 300,
}

BOARD_SIZE = 12
MAX_L1_DISTANCE = (BOARD_SIZE - 1) * 2
DISTANCE_WEIGHT = 0.2
CAPTURE_WEIGHT = 0.3
RECAPTURE_PENALTY_WEIGHT = 1.0
CAPTURE_VALUE_DIFF_WEIGHT = 0.1
OPEN_MOVE_WEIGHT = 0.2


def mobility_score(game_state: GameState):
    """White-centric mobility term based on own_legal_moves - opp_legal_moves."""
    own_side = game_state.side
    opp_side = 1 - own_side
    own_moves = rule.countMovesBySide(game_state, own_side)
    opp_moves = rule.countMovesBySide(game_state, opp_side)
    mobility_delta = own_moves - opp_moves

    # Keep evaluation white-centric regardless of side-to-move.
    if own_side == 1:
        mobility_delta = -mobility_delta

    return mobility_delta * OPEN_MOVE_WEIGHT


def material_score(game_state: GameState):
    """White-centric material score."""
    score = 0
    for piece, loc_set in game_state.pieces.items():
        if not loc_set:
            continue
        value = PIECES_VALUES[piece.upper()] * len(loc_set)
        if piece.isupper():
            score += value
        else:
            score -= value
    return score


def distance_to_opponent_prince_score(game_state: GameState, last_move=None):
    """Reward last moved piece for getting closer to opponent prince."""
    if last_move is None:
        return 0

    board = game_state.board
    _, (dest_r, dest_c) = last_move
    moved_piece = board[dest_r][dest_c]
    if moved_piece == ".":
        return 0

    if moved_piece.isupper():
        opponent_prince_positions = game_state.pieces.get("p")
        if not opponent_prince_positions:
            return 0
        prince_r, prince_c = next(iter(opponent_prince_positions))
        dist = abs(dest_r - prince_r) + abs(dest_c - prince_c)
        return DISTANCE_WEIGHT * (MAX_L1_DISTANCE - dist)

    opponent_prince_positions = game_state.pieces.get("P")
    if not opponent_prince_positions:
        return 0
    prince_r, prince_c = next(iter(opponent_prince_positions))
    dist = abs(dest_r - prince_r) + abs(dest_c - prince_c)
    return -DISTANCE_WEIGHT * (MAX_L1_DISTANCE - dist)


def _apply_move_inplace(board, pieces, move):
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
    return src_piece, dest_piece


def _undo_move_inplace(board, pieces, move, src_piece, dest_piece):
    src, dest = move
    src_r, src_c = src
    dest_r, dest_c = dest

    pieces[src_piece].remove(dest)
    pieces[src_piece].add(src)
    if dest_piece != ".":
        pieces[dest_piece].add(dest)

    board[src_r][src_c] = src_piece
    board[dest_r][dest_c] = dest_piece


def _has_immediate_recapture(board, pieces, side, capture_move, capture_square):
    src_piece, dest_piece = _apply_move_inplace(board, pieces, capture_move)
    try:
        if dest_piece in ("P", "p"):
            return False
        state_after_capture = GameState(board, pieces, 0, 1 - side, None)
        for reply_move in rule.generatemoves(state_after_capture):
            if reply_move[1] == capture_square:
                return True
        return False
    finally:
        _undo_move_inplace(board, pieces, capture_move, src_piece, dest_piece)


def capture_setup_score(game_state: GameState, last_move=None):
    """Evaluate how much immediate capture potential the last moved piece creates."""
    if last_move is None:
        return 0

    board = game_state.board
    _, (dest_r, dest_c) = last_move
    moved_piece = board[dest_r][dest_c]
    if moved_piece == ".":
        return 0

    side = 0 if moved_piece.isupper() else 1
    potential_moves = []
    move_fn = rule.move_functions.get(moved_piece.upper())
    if move_fn is None:
        return 0

    move_fn(board, side, (dest_r, dest_c), potential_moves)

    moved_piece_value = PIECES_VALUES[moved_piece.upper()]
    best_score = 0
    for _, (target_r, target_c) in potential_moves:
        target_piece = board[target_r][target_c]
        is_enemy_capture = (side == 0 and target_piece.islower()) or (side == 1 and target_piece.isupper())
        if not is_enemy_capture:
            continue

        capture_move = ((dest_r, dest_c), (target_r, target_c))
        recaptured = _has_immediate_recapture(
            board,
            game_state.pieces,
            side,
            capture_move,
            (target_r, target_c),
        )

        captured_value = PIECES_VALUES[target_piece.upper()]
        recapture_loss = moved_piece_value if recaptured else 0
        value_diff = captured_value - moved_piece_value
        diff_reward = CAPTURE_VALUE_DIFF_WEIGHT * value_diff

        if side == 0:
            capture_component = captured_value - (RECAPTURE_PENALTY_WEIGHT * recapture_loss)
            candidate_score = (CAPTURE_WEIGHT * capture_component) + diff_reward
            best_score = max(best_score, candidate_score)
        else:
            capture_component = -captured_value + (RECAPTURE_PENALTY_WEIGHT * recapture_loss)
            candidate_score = (CAPTURE_WEIGHT * capture_component) - diff_reward
            best_score = min(best_score, candidate_score)

    return best_score


def evaluation_function(game_state: GameState, last_move=None):
    # White-centric score composed from independent heuristics.
    score = 0
    score += material_score(game_state)
    score += mobility_score(game_state)
    score += distance_to_opponent_prince_score(game_state, last_move)
    score += capture_setup_score(game_state, last_move)
    return score
