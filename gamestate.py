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

    def undo(self):
        self.board.undo()
        self.current_player *= -1
    def reset(self):
        self.board.reset()
        self.current_player = BLACK
