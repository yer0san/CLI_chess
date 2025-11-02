"""
CLI Chess Game using python-chess (no engine)

Features:
- Two-player local play (White vs Black)
- Accepts UCI (e2e4) or SAN (Nf3, O-O) notation
- undo, legal, show, save, load, flip board orientation
- Save/Load PGN files
"""

import chess
import chess.pgn
import datetime


def print_help():
    print("""
Commands:
  <move>        Make a move. Accepts UCI (e2e4) or SAN (Nf3, O-O) notation.
  undo          Undo last move.
  legal         Show all legal moves.
  show          Print the board.
  save <file>   Save the current game to a PGN file.
  load <file>   Load a PGN file (replaces current game).
  flip          Flip board orientation.
  help          Show this help message.
  quit / exit   Exit the game.
""")


def print_board(board, flipped=False):
    """Print ASCII board."""
    if flipped:
        ranks = range(1, 9)
        files = range(8, 0, -1)
    else:
        ranks = range(8, 0, -1)
        files = range(1, 9)

    def square_name(file_i, rank_i):
        return chess.square_name(chess.square(file_i - 1, rank_i - 1))

    print("\n  +------------------------+")
    for r in ranks:
        row = []
        for f in files:
            sq = square_name(f, r)
            piece = board.piece_at(chess.parse_square(sq))
            row.append(piece.symbol() if piece else ".")
        print(f"{r} | {' '.join(row)} |")
    print("  +------------------------+")
    print("    " + " ".join(chess.FILE_NAMES if not flipped else reversed(chess.FILE_NAMES)))
    print(f"\nTurn: {'White' if board.turn == chess.WHITE else 'Black'}")

    if board.is_check():
        print("Check!")
    if board.is_checkmate():
        print("Checkmate!")
    if board.is_stalemate():
        print("Stalemate!")
    if board.is_insufficient_material():
        print("Draw by insufficient material.")
    print()


def save_pgn(board, filename, white="White", black="Black", event="CLI Chess"):
    """Save current game to PGN file."""
    game = chess.pgn.Game()
    game.headers["Event"] = event
    game.headers["Date"] = datetime.datetime.now().strftime("%Y.%m.%d")
    game.headers["White"] = white
    game.headers["Black"] = black

    node = game
    for mv in board.move_stack:
        node = node.add_variation(mv)
    game.headers["Result"] = board.result() if board.is_game_over() else "*"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(game))
    print(f"Game saved to {filename}")


def load_pgn(filename):
    """Load a PGN file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            game = chess.pgn.read_game(f)
            if not game:
                print("No valid game found in file.")
                return None
            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
            print(f"Loaded game from {filename}")
            return board
    except FileNotFoundError:
        print("File not found:", filename)
        return None
    except Exception as e:
        print("Failed to load PGN:", e)
        return None


def main():
    board = chess.Board()
    flipped = False

    print("Welcome to CLI Chess (python-chess)")
    print("Type 'help' for available commands.\n")

    print_board(board, flipped)

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if raw == "":
            continue

        parts = raw.split()
        cmd = parts[0].lower()

        if cmd in ("quit", "exit"):
            print("Goodbye.")
            break
        elif cmd == "help":
            print_help()
            continue
        elif cmd == "show":
            print_board(board, flipped)
            continue
        elif cmd == "undo":
            if len(board.move_stack) > 0:
                board.pop()
                print("Last move undone.")
                print_board(board, flipped)
            else:
                print("No moves to undo.")
            continue
        elif cmd == "legal":
            legal = list(board.legal_moves)
            print("Legal moves:", " ".join(m.uci() for m in legal))
            continue
        elif cmd == "flip":
            flipped = not flipped
            print_board(board, flipped)
            continue
        elif cmd == "save":
            if len(parts) < 2:
                print("Usage: save <filename.pgn>")
                continue
            save_pgn(board, parts[1])
            continue
        elif cmd == "load":
            if len(parts) < 2:
                print("Usage: load <filename.pgn>")
                continue
            new_board = load_pgn(parts[1])
            if new_board:
                board = new_board
                print_board(board, flipped)
            continue

        # Otherwise, interpret as move input
        move = None
        try:
            # Try SAN first (e.g., Nf3)
            move = board.parse_san(raw)
        except Exception:
            try:
                # Then try UCI (e.g., e2e4)
                move = chess.Move.from_uci(raw)
                if move not in board.legal_moves:
                    print("Illegal move.")
                    continue
            except Exception:
                print("Invalid move format. Try SAN (Nf3) or UCI (e2e4).")
                continue

        board.push(move)
        print_board(board, flipped)

        # Check for game end
        if board.is_checkmate():
            print("Checkmate! Result:", board.result())
        elif board.is_stalemate():
            print("Stalemate! Result:", board.result())
        elif board.is_insufficient_material():
            print("Draw by insufficient material.")
        elif board.can_claim_fifty_moves():
            print("Draw (50-move rule claimable).")
        elif board.can_claim_threefold_repetition():
            print("Draw (threefold repetition claimable).")


if __name__ == "__main__":
    main()
