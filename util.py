class inputData:
    def __init__(self, side:str, ownTime:str, otherTime:str, board:list[list[str]], pieces:dict[str, set[tuple[int, int]]]):
        self.side = side
        self.ownTime = ownTime
        self.otherTime = otherTime
        self.board = board
        self.pieces = pieces


def read_file()->inputData:
    with open("input.txt") as file:
        lines = file.readlines()
        ownSide = lines[0].strip()
        ownTime,otherTime = map(str.strip, lines[1].split())
        board = []
        pieces = {}
        for i in range(0, 12):
            row = list(lines[i+2].strip())
            for p in range(12):
                piece = row[p]
                if piece != ".":
                    if piece not in pieces:
                        pieces[piece] = set()
                    pieces[piece].add((i,p))
            board.append(row)
        return inputData(ownSide, ownTime, otherTime, board, pieces)

COLS = "abcdefghjkmn"  # note: skips i and l (12 columns)

def to_coord(r, c):
    # If your output uses 1-based rows, add 1.
    return f"{COLS[c]}{12-r}"

def write_output_move(move):
    (r1, c1), (r2, c2) = move
    print(f"Agent chose move: {to_coord(r1,c1)} {to_coord(r2,c2)}")

    with open("output.txt", "w") as f:
        f.write(f"{to_coord(r1,c1)} {to_coord(r2,c2)}\n")

def append_output_move(move):
    (r1, c1), (r2, c2) = move
    print(f"Agent chose move: {to_coord(r1,c1)} {to_coord(r2,c2)}")

    with open("append.txt", "w") as f:
        f.write(f"{to_coord(r1,c1)} {to_coord(r2,c2)}\n")



    