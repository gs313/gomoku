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

        # self.active_cells = set()
        self.active_cells = {}  # (x,y) → count

    def reset(self):
        self.black_bits = 0
        self.white_bits = 0

        self.moves = []
        self.captures = {BLACK: 0, WHITE: 0}
        self.last_move = None

        # self.active_cells = set()
        self.active_cells = {}  # (x,y) → count

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

    def _count_free_threes_simulated(self, x, y, player, captured):
        move_bit = 1 << idx(x, y)

        player_bits = self.get_bits(player) | move_bit
        opponent = -player
        opponent_bits = self.get_bits(opponent)

        for cx, cy in captured:
            opponent_bits &= ~(1 << idx(cx, cy))

        def is_player(nx, ny):
            return player_bits & (1 << idx(nx, ny))

        def is_empty(nx, ny):
            bit = 1 << idx(nx, ny)
            return not (player_bits & bit or opponent_bits & bit)

        def is_free_three_dir(dx, dy):
            line = []

            for i in range(-4, 5):
                nx = x + i*dx
                ny = y + i*dy

                if not self._inside(nx, ny):
                    line.append(2)
                elif is_player(nx, ny):
                    line.append(1)
                elif is_empty(nx, ny):
                    line.append(0)
                else:
                    line.append(2)

            center = 4

            patterns = [
                [0,1,1,1,0],
                [0,1,1,0,1,0],
                [0,1,0,1,1,0],
            ]

            for p in patterns:
                L = len(p)
                for i in range(len(line) - L + 1):
                    if line[i:i+L] == p:
                        if i <= center < i + L:
                            return True

            return False

        count = 0
        for dx, dy in [(1,0), (0,1), (1,1), (1,-1)]:
            if is_free_three_dir(dx, dy):
                count += 1

        return count
    def is_legal_move(self, x, y, player):
        if self.has_stone(x, y):
            return False

        # simulate capture WITHOUT modifying board
        captured = self._get_captures_preview(x, y, player)

        free_threes = self._count_free_threes_simulated(x, y, player, captured)

        if free_threes >= 2 and len(captured) == 0:
            return False

        return True
    def play(self, x, y, player):
        if not self.is_legal_move(x, y, player):
            # print(f"This print in play.. not legal {player}")
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

        # self.moves.append((x, y, player, captured))
        self.last_move = (x, y)

        # self._update_active_cells(x, y)
        added_cells = self._update_active_cells(x, y)

        self.moves.append((x, y, player, captured, added_cells))

        return True

    def undo(self):
        if not self.moves:
            return

        # x, y, player, captured = self.moves.pop()
        x, y, player, captured, added_cells = self.moves.pop()
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
        for cell in added_cells:
            if cell in self.active_cells:
                self.active_cells[cell] -= 1
                if self.active_cells[cell] <= 0:
                    del self.active_cells[cell]
        # remove the actual move position if present
        if (x, y) in self.active_cells:
            self.active_cells.pop((x, y), None)

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

    def _get_captures_preview(self, x, y, player):
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

            # must stay inside board
            if not (0 <= x3 < SIZE and 0 <= y3 < SIZE):
                continue

            # check pattern: player - opponent - opponent - player
            if (self._is_opponent(x1, y1, opponent) and
                self._is_opponent(x2, y2, opponent) and
                self._is_player(x3, y3, player)):

                captured.append((x1, y1))
                captured.append((x2, y2))

        return captured

    def _is_opponent(self, x, y, opponent):
        bit = 1 << idx(x, y)
        if opponent == BLACK:
            return self.black_bits & bit
        else:
            return self.white_bits & bit

    def _remove_stone(self, x, y, player):
        bit = ~(1 << idx(x, y))
        if player == BLACK:
            self.black_bits &= bit
        else:
            self.white_bits &= bit
    def get_capture_counts(self):
        return self.captures[BLACK], self.captures[WHITE]


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
        line = []

        for i in range(-4, 5):
            nx = x + i*dx
            ny = y + i*dy

            if not self._inside(nx, ny):
                line.append(2)  # blocked
            elif self._is_empty(nx, ny):
                line.append(0)
            elif self._is_player(nx, ny, player):
                line.append(1)
            else:
                line.append(2)

        center = 4  # index of (x, y)

        # patterns (as numeric)
        patterns = [
            [0,1,1,1,0],        # _XXX_
            [0,1,1,0,1,0],      # _XX_X_
            [0,1,0,1,1,0],      # _X_XX_
        ]

        for p in patterns:
            L = len(p)
            for i in range(len(line) - L + 1):
                if line[i:i+L] == p:
                    if i <= center < i + L:  # must include new move
                        return True

        return False

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

    # def _update_active_cells(self, x, y):
    #     for dx in range(-2, 3):
    #         for dy in range(-2, 3):
    #             nx, ny = x + dx, y + dy
    #             if 0 <= nx < SIZE and 0 <= ny < SIZE:
    #                 self.active_cells.add((nx, ny))

    # def get_candidate_moves(self):
    #     if not self.moves:
    #         return [(SIZE//2, SIZE//2)]

    #     return [(x, y) for (x, y) in self.active_cells if not self.has_stone(x, y)]

    # def get_candidate_moves(self):
    #     if not self.moves:
    #         return [(SIZE//2, SIZE//2)]

    #     candidates = set()

    #     for (x, y, _, _) in self.moves:
    #         for dx in range(-1, 2):
    #             for dy in range(-1, 2):
    #                 nx, ny = x + dx, y + dy
    #                 if 0 <= nx < SIZE and 0 <= ny < SIZE:
    #                     if not self.has_stone(nx, ny):
    #                         candidates.add((nx, ny))

    #     return list(candidates)

    def _update_active_cells(self, x, y):
        added = []

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                nx, ny = x + dx, y + dy
                if 0 <= nx < SIZE and 0 <= ny < SIZE:

                    if not self.has_stone(nx, ny):
                        if (nx, ny) not in self.active_cells:
                            self.active_cells[(nx, ny)] = 1
                            added.append((nx, ny))
                        else:
                            self.active_cells[(nx, ny)] += 1

        return added
    def get_candidate_moves(self):
        if not self.moves:
            return [(SIZE//2, SIZE//2)]

        return list(self.active_cells.keys())
        # # ========================
#   Check Win
# =========================

    def _can_break_five_by_capture(self, player):
        opponent = -player

        # try all opponent moves
        for (x, y) in self.get_candidate_moves():
            if not self.is_legal_move(x, y, opponent):
                continue

            if not self.play(x, y, opponent):
                continue

            # if this capture breaks the 5
            still_five = self._check_from(*self.last_move, player)

            captured = len(self.moves[-1][3]) > 0

            self.undo()

            # capture happened AND breaks the line
            if captured and not still_five:
                return True

        return False
    def check_win(self, player,fast=False):
        opponent = -player

        # Capture win
        if self.captures[player] >= 5:
            return True
        #  Line win (needs validation)
        if self.last_move:
            x, y = self.last_move

            if self._is_player(x, y, player):
                if fast:
                    return self._check_from(x, y, player)
                if self._check_from(x, y, player):

                    # 🚨 check if opponent can break it
                    if self._can_break_five_by_capture(player):

                        # 💀 if opponent already has 4 captures → they win
                        if self.captures[opponent] >= 4:
                            return False  # player does NOT win

                        # otherwise: not a valid win yet
                        return False

                    # ✅ unbreakable → real win
                    return True

        return False
    # def check_win(self, player):
    #     # 🏆 Capture win
    #     if self.captures[player] >= 5:
    #         return True

    #     # 🏆 Line win (only check last move)
    #     if self.last_move:
    #         x, y = self.last_move
    #         if self._is_player(x, y, player):
    #             return self._check_from(x, y, player)

    #     return False

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
