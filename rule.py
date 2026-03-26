from state import GameState

def add_move(moves, src, dst, pieceName):
    move = (src, dst)
    moves.append(move)
    #print(f"added move {move} for piece {pieceName}")

def babymove(board, side, loc ,moves):
    if side == 0:
        isFriendly = str.isupper
    else:       
        isFriendly = str.islower
    directions = [
                (-1,0),(-2,0),  # Up by 1,2
                (1,0),(2,0)     # Down by 1,2
                ]   
    r,c = loc
    if side == 0: # white's turn
        for dr,dc in directions[:2]: # white's moves
            new_r, new_c = r + dr, c + dc
            if 0 <= new_r < 12 and 0 <= new_c < 12 and not isFriendly(board[new_r][new_c]):
                if dr == -2: # check intermediate square for move by 2
                    if board[r-1][c] == ".":
                        #print(f"added baby move from {r},{c} to {new_r},{new_c}")
                        add_move(moves, (r, c), (new_r, new_c), "Baby")
                else:
                    #print(f"added baby move from {r},{c} to {new_r},{new_c}")
                    add_move(moves, (r, c), (new_r, new_c), "Baby")

    else: # black's turn
        for dr,dc in directions[2:]: # black's moves
            new_r, new_c = r + dr, c + dc
            if 0 <= new_r < 12 and 0 <= new_c < 12 and not isFriendly(board[new_r][new_c]):
                if dr == 2: # check intermediate square for move by 2
                    if board[r+1][c] == ".":
                        add_move(moves, (r, c), (new_r, new_c),"Baby")
                        
                else:
                    add_move(moves, (r, c), (new_r, new_c), "Baby")
                     
def princemove(board, side, loc, moves):
    directions = [
        (-1, 0),    # Up
        (1, 0),     #Down
        (0, 1),     # Right
        (0, -1),    # Left
        (-1, 1),    # Up Right
        (-1, -1),   # Up Left
        (1, 1),     # Down Right
        (1, -1)     # Down Left
    ]
    if side == 0:
        isFriendly = str.isupper
    else:
        isFriendly = str.islower
    r,c = map(int, loc)

    for dr,dc in directions:
        new_r, new_c = r + dr, c + dc
        if 0 <= new_r < 12 and 0 <= new_c < 12 and not isFriendly(board[new_r][new_c]):
            add_move(moves, (r, c), (new_r, new_c),"Prince")
   
def princessmove(board, side, loc, moves):
    directions = [
        (-1, 0),    # Ups
        (1, 0),     #Down
        (0, 1),     # Right
        (0, -1),    # Left
        (-1, 1),    # Up Right
        (-1, -1),   # Up Left
        (1, 1),     # Down Right
        (1, -1)     # Down Left
    ]
    if side == 0:
        isFriendly = str.isupper
    else:
        isFriendly = str.islower
    r,c = map(int, loc)
    for dr,dc in directions:
        for n in range(1,4):
            new_r, new_c = r + n*dr, c + n*dc
            if not (0 <= new_r < 12 and 0 <= new_c < 12):
                break
            if isFriendly(board[new_r][new_c]):
                break
            add_move(moves, (r, c), (new_r, new_c), "Princess")
            if board[new_r][new_c] != ".":
                break

                    

def ponymove(board, side, loc, moves):
    directions=[
        (1,1),
        (1,-1),
        (-1,1),
        (-1,-1)
    ]
    if side ==0:
        isFriendly = str.isupper
    else:
        isFriendly = str.islower
    r,c = map(int,loc)

    for dr,dc in directions:
        new_r, new_c = r+dr, c+dc
        if 0<=new_r< 12 and 0 <= new_c < 12 and not isFriendly(board[new_r][new_c]):
            add_move(moves, (r, c), (new_r, new_c), "Pony")
    

def guardmove(board, side, loc, moves):
    directions = [
        (1,0),(2,0),    # white: down by 1,2; black: up by 1,2
        (-1,0),(-2,0),  # white: up by 1,2; black: down by 1,2
        (0,1),(0,2),    # white: right by 1,2; black: left by 1,2
        (0,-1),(0,-2)   # white: left by 1,2; black: right by 1,2
    ]
    r,c = map(int,loc)
    if side == 0:
        isFriendly = str.isupper
    else:
        isFriendly = str.islower
    
    for dr,dc in directions:
        new_r, new_c = r+dr, c+dc
        if 0<=new_r< 12 and 0 <= new_c < 12 and not isFriendly(board[new_r][new_c]):
            #print(f"Is friendly: {isFriendly(board[new_r][new_c])}")
            if dr == 2: # check intermediate square for move by 2
                if board[r+1][c] == ".":
                    add_move(moves, (r, c), (new_r, new_c), "Guard")
            elif dr == -2:
                if board[r-1][c] == ".":
                    add_move(moves, (r, c), (new_r, new_c), "Guard")
            elif dc == 2:
                if board[r][c+1] == ".":
                    add_move(moves, (r, c), (new_r, new_c), "Guard")
            elif dc == -2:
                if board[r][c-1] == ".":
                    add_move(moves, (r, c), (new_r, new_c), "Guard")
            else: # move by 1
                add_move(moves, (r, c), (new_r, new_c), "Guard")

def tutormove(board, side, loc, moves):
    directions=[
        (1,1),(2,2),    # Down Right
        (1,-1),(2,-2),  # Down Left
        (-1,1),(-2,2),  # Up Right
        (-1,-1),(-2,-2) # Up Left
    ]
    if side ==0:
        isFriendly = str.isupper
    else:
        isFriendly = str.islower
    r,c = map(int,loc)

    for dr,dc in directions:
        new_r, new_c = r+dr, c+dc
        if 0<=new_r< 12 and 0 <= new_c < 12 and not isFriendly(board[new_r][new_c]):
            if dr == 2 and dc == 2: # check intermediate square for move by 2
                if board[r+1][c+1] == ".":
                    add_move(moves, (r, c), (new_r, new_c), "Tutor")
            elif dr == 2 and dc == -2:
                if board[r+1][c-1] == ".":
                    add_move(moves, (r, c), (new_r, new_c), "Tutor")
            elif dr == -2 and dc == 2:
                    if board[r-1][c+1] == ".":
                        add_move(moves, (r, c), (new_r, new_c), "Tutor")
            elif dr == -2 and dc == -2:
                if board[r-1][c-1] == ".":
                    add_move(moves, (r, c), (new_r, new_c), "Tutor")
            else: # move by 1
                add_move(moves, (r, c), (new_r, new_c), "Tutor")

def scoutmove(board, side, loc, moves):
    isFriendly = str.isupper if side == 0 else str.islower
    forward = -1 if side == 0 else 1  # white up, black down

    r, c = loc  # loc should already be (int,int); don't map(int,loc) unless needed

    # Generate forward-only offsets
    for k in (1, 2, 3):
        for dc in (0, 1, -1):   # straight, diag-right, diag-left
            nr = r + forward * k
            nc = c + dc
            if 0 <= nr < 12 and 0 <= nc < 12 and not isFriendly(board[nr][nc]):
                # If jumping is allowed, no path check needed.
                add_move(moves, (r, c), (nr, nc), "Scout")
           

def siblingmove(board, side, loc, moves):
    directions = [
        (-1, 0),    # Up
        (1, 0),     #Down
        (0, 1),     # Right
        (0, -1),    # Left
        (-1, 1),    # Up Right
        (-1, -1),   # Up Left
        (1, 1),     # Down Right
        (1, -1)     # Down Left
    ]
    if side == 0:
        isFriendly = str.isupper
    else:
        isFriendly = str.islower
    r,c = map(int, loc)
    
    for dr,dc in directions:
        new_r, new_c = r + dr, c + dc
        if 0 <= new_r < 12 and 0 <= new_c < 12 and not isFriendly(board[new_r][new_c]):
            # Check adjacent friendly units for sibling move
            for adj_dr, adj_dc in directions:
                adj_r, adj_y = new_r + adj_dr, new_c + adj_dc
                # Check if adjacent square is within bounds and has a friendly unit
                if 0 <= adj_r < 12 and 0 <= adj_y < 12 and isFriendly(board[adj_r][adj_y]):
                    if (adj_r, adj_y) != (r, c): # Prevent validating against itself
                        add_move(moves, (r, c), (new_r, new_c),"Slibling")
                        break

move_functions = {
    'P': princemove,
    'B': babymove,
    'S': scoutmove,
    'G': guardmove,
    'T': tutormove,
    'Y': ponymove,
    'N': siblingmove,
    'X': princessmove
}

def generatemoves(state: GameState):
    board = state.board
    side = state.side
    pieces = state.pieces
    moves= []

    for key, loc_set in pieces.items():
        #print(f"key is {key}")
        if state.side == 0 and not key.isupper():
            continue
        elif state.side == 1 and not key.islower():
            continue
  
        fn = move_functions.get(key.upper())

        for loc in loc_set:
            fn(board, side, loc, moves)

    return moves

def countMoves(state: GameState):
    """Count available moves without generating the full list."""
    board = state.board
    side = state.side
    pieces = state.pieces
    move_count = 0

    for key, loc_set in pieces.items():
        if state.side == 0 and not key.isupper():
            continue
        elif state.side == 1 and not key.islower():
            continue
  
        fn = move_functions.get(key.upper())

        for loc in loc_set:
            # Pass a counter instead of a list
            move_count += countMovesForPiece(board, side, loc, fn)

    return move_count

def countMovesForPiece(board, side, loc, move_fn):
    """Helper: count moves for a single piece without appending."""
    moves = []
    move_fn(board, side, loc, moves)  # Still uses existing move_fn
    return len(moves)