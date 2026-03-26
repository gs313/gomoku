SIZE = 19
EMPTY = 0
BLACK = 1
WHITE = -1


def idx(x, y):
    return x * SIZE + y


def coord(i):
    return (i // SIZE, i % SIZE)


class Board:
    def __init__(self):
        self.black_bits = 0
        self.white_bits = 0

        self.moves = []
        self.captures = {BLACK: 0, WHITE: 0}
        self.last_move = None

        self.active_cells = set()

    # =========================
    # BASIC
    # =========================

    def has_stone(self, x, y):
        bit = 1 << idx(x, y)
        return (self.black_bits | self.white_bits) & bit

    def get_bits(self, player):
        return self.black_bits if player == BLACK else self.white_bits

    # =========================
    # PLAY / UNDO
    # =========================

    def play(self, x, y, player):
        if self.has_stone(x, y):
            return False

        move = idx(x, y)
        bit = 1 << move

        if player == BLACK:
            self.black_bits |= bit
        else:
            self.white_bits |= bit

        # captures
        captured = self._apply_captures(x, y, player)

        self.moves.append((x, y, player, captured))
        self.last_move = (x, y)

        self._update_active_cells(x, y)

        return True

    def undo(self):
        if not self.moves:
            return

        x, y, player, captured = self.moves.pop()
        move = idx(x, y)
        bit_mask = ~(1 << move)

        if player == BLACK:
            self.black_bits &= bit_mask
        else:
            self.white_bits &= bit_mask

        # restore captures
        for cx, cy in captured:
            bit = 1 << idx(cx, cy)
            if player == BLACK:
                self.white_bits |= bit
            else:
                self.black_bits |= bit

        self.captures[player] -= len(captured) // 2
        self.last_move = self.moves[-1][:2] if self.moves else None

    # =========================
    # CAPTURES
    # =========================

    def _apply_captures(self, x, y, player):
        opponent = -player
        captured = []

        directions = [
            (1,0), (0,1), (1,1), (1,-1),
            (-1,0), (0,-1), (-1,-1), (-1,1)
        ]

        for dx, dy in directions:
            x1, y1 = x + dx, y + dy
            x2, y2 = x + 2*dx, y + 2*dy
            x3, y3 = x + 3*dx, y + 3*dy

            if not (0 <= x3 < SIZE and 0 <= y3 < SIZE):
                continue

            if (self.has_stone(x1, y1) and
                self.has_stone(x2, y2) and
                self.has_stone(x3, y3)):

                if (self.get_bits(opponent) & (1 << idx(x1, y1)) and
                    self.get_bits(opponent) & (1 << idx(x2, y2)) and
                    self.get_bits(player) & (1 << idx(x3, y3))):

                    # capture
                    self._remove_stone(x1, y1, opponent)
                    self._remove_stone(x2, y2, opponent)

                    captured.append((x1, y1))
                    captured.append((x2, y2))

        self.captures[player] += len(captured) // 2
        return captured

    def _remove_stone(self, x, y, player):
        bit = ~(1 << idx(x, y))
        if player == BLACK:
            self.black_bits &= bit
        else:
            self.white_bits &= bit

    # =========================
    # ACTIVE CELLS
    # =========================

    def _update_active_cells(self, x, y):
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                nx, ny = x + dx, y + dy
                if 0 <= nx < SIZE and 0 <= ny < SIZE:
                    self.active_cells.add((nx, ny))

    def get_candidate_moves(self):
        if not self.moves:
            return [(SIZE//2, SIZE//2)]

        return [(x, y) for (x, y) in self.active_cells if not self.has_stone(x, y)]
