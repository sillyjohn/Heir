from typing import List, Dict, Set, Tuple

PLAYDATA_FILE = "playdata.txt"

class inputData:
    def __init__(self, side:str, ownTime:str, otherTime:str, board:List[List[str]], pieces:Dict[str, Set[Tuple[int, int]]]):
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

def _read_playdata() -> Tuple[int, Dict[int, int]]:
    round_num = 0
    counts: Dict[int, int] = {}

    try:
        with open(PLAYDATA_FILE, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return round_num, counts

    if not lines:
        return round_num, counts

    # Backward compatible: first line remains round number.
    try:
        round_num = int(lines[0])
        history_lines = lines[1:]
    except ValueError:
        # If old/corrupted format, treat all lines as history and keep round 0.
        history_lines = lines

    for line in history_lines:
        parts = line.split()
        if len(parts) == 2:
            key_token, count_token = parts
        elif len(parts) == 3 and parts[0] == "H":
            _, key_token, count_token = parts
        else:
            continue
        try:
            pos_key = int(key_token)
            count = int(count_token)
        except ValueError:
            continue
        if count > 0:
            counts[pos_key] = count

    return round_num, counts


def _write_playdata(round_num: int, counts: Dict[int, int]) -> None:
    with open(PLAYDATA_FILE, "w") as f:
        f.write(f"{round_num}\n")
        for pos_key in sorted(counts):
            count = counts[pos_key]
            if count > 0:
                f.write(f"{pos_key} {count}\n")


def get_round_count() -> int:
    round_num, _ = _read_playdata()
    return round_num


def countRound():
    round_num, counts = _read_playdata()
    round_num += 1
    _write_playdata(round_num, counts)


def load_position_counts() -> Dict[int, int]:
    _, counts = _read_playdata()
    return counts


def save_position_counts(counts: Dict[int, int]) -> None:
    round_num, _ = _read_playdata()
    _write_playdata(round_num, counts)


def clear_position_counts() -> None:
    round_num, _ = _read_playdata()
    _write_playdata(round_num, {})


def increment_position_count(counts: Dict[int, int], pos_key: int) -> None:
    counts[pos_key] = counts.get(pos_key, 0) + 1
