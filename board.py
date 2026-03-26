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

        # place
        if player == BLACK:
            self.black_bits |= bit
        else:
            self.white_bits |= bit

        # apply captures first
        captured = self._apply_captures(x, y, player)

        # check double-three AFTER captures
        free_threes = self._count_free_threes(x, y, player)

        if free_threes >= 2:
            # undo placement
            if player == BLACK:
                self.black_bits &= ~bit
            else:
                self.white_bits &= ~bit

            # undo captures
            for cx, cy in captured:
                restore_bit = 1 << idx(cx, cy)
                if player == BLACK:
                    self.white_bits |= restore_bit
                else:
                    self.black_bits |= restore_bit

            self.captures[player] -= len(captured) // 2

            return False

        # accept move
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
    # DOUBLE THREES
    # =========================

    def _count_free_threes(self, x, y, player):
        count = 0

        directions = [(1,0), (0,1), (1,1), (1,-1)]

        for dx, dy in directions:
            if self._is_free_three(x, y, dx, dy, player):
                count += 1

        return count

    def _is_free_three(self, x, y, dx, dy, player):
        stones = 1
        open_ends = 0

        # forward
        nx, ny = x + dx, y + dy
        while self._inside(nx, ny):
            if self._is_player(nx, ny, player):
                stones += 1
                nx += dx
                ny += dy
            elif self._is_empty(nx, ny):
                open_ends += 1
                break
            else:
                break

        # backward
        nx, ny = x - dx, y - dy
        while self._inside(nx, ny):
            if self._is_player(nx, ny, player):
                stones += 1
                nx -= dx
                ny -= dy
            elif self._is_empty(nx, ny):
                open_ends += 1
                break
            else:
                break

        return stones == 3 and open_ends == 2

    def _inside(self, x, y):
        return 0 <= x < 19 and 0 <= y < 19


    def _is_empty(self, x, y):
        return not self.has_stone(x, y)


    def _is_player(self, x, y, player):
        bit = 1 << (x * 19 + y)
        if player == 1:
            return self.black_bits & bit
        else:
            return self.white_bits & bit
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

    def check_win(self, player):
        for (x, y, p, _) in self.moves:
            if p != player:
                continue

            if self._check_from(x, y, player):
                return True

        return False


    def _check_from(self, x, y, player):
        directions = [(1,0), (0,1), (1,1), (1,-1)]

        for dx, dy in directions:
            count = 1

            # forward
            nx, ny = x + dx, y + dy
            while self._inside(nx, ny) and self._is_player(nx, ny, player):
                count += 1
                nx += dx
                ny += dy

            # backward
            nx, ny = x - dx, y - dy
            while self._inside(nx, ny) and self._is_player(nx, ny, player):
                count += 1
                nx -= dx
                ny -= dy

            if count >= 5:
                return True

        return False
