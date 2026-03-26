class GameState:
    BOARD_SIZE = 19

    def __init__(self):
        self.black = 0
        self.white = 0
        self.current_player = 1  # 1 = black, -1 = white

    def pos_to_bit(self, x, y):
        return x * self.BOARD_SIZE + y

    def has_stone(self, x, y):
        bit = 1 << self.pos_to_bit(x, y)
        return (self.black & bit) or (self.white & bit)

    def put(self, x, y):
        if self.has_stone(x, y):
            return False

        bit = 1 << self.pos_to_bit(x, y)

        if self.current_player == 1:
            self.black |= bit
        else:
            self.white |= bit

        self.current_player *= -1
        return True

    def undo(self, x, y):
        bit = 1 << self.pos_to_bit(x, y)

        if self.black & bit:
            self.black &= ~bit
        elif self.white & bit:
            self.white &= ~bit

        self.current_player *= -1