from board import Board, BLACK, WHITE


class GameState:
    BOARD_SIZE = 19

    def __init__(self):
        self.board = Board()
        self.current_player = BLACK

    # =========================
    # UI COMPATIBILITY
    # =========================

    @property
    def black(self):
        return self.board.black_bits

    @property
    def white(self):
        return self.board.white_bits

    # =========================
    # GAME ACTIONS
    # =========================

    def has_stone(self, x, y):
        return self.board.has_stone(x, y)

    def put(self, x, y):
        if not self.board.play(x, y, self.current_player):
            return False

        self.current_player *= -1
        return True
    def is_legal_rule(self, x, y, move_count, rule):
        center = self.BOARD_SIZE // 2
        print(f"Checking rule for move {move_count} at ({x}, {y}) under rule '{rule}'")
        if rule == "pro":
            if move_count == 0:
                return x == center and y == center , "First move must be at the center"

            if move_count == 2:
                if abs(x - center) <= 2 and abs(y - center) <= 2:
                    return False , "Third move cannot be within 3x3 area of the center"
            return True, None

    def undo(self):
        self.board.undo()
        self.current_player *= -1
    def reset(self):
        self.board.reset()
        self.current_player = BLACK
