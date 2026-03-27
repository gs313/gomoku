from board import BLACK, WHITE


class Heuristic:
    def __init__(self, board):
        self.board = board

    # =========================
    # MAIN EVALUATION
    # =========================

    def evaluate(self, player):
        opponent = -player

        #  Immediate win / loss detection
        if self.board.check_win(player):
            return 10**9
        if self.board.check_win(opponent):
            return -10**9

        if self.board.captures[player] >= 8:
            return 5 * 10**8   # almost winning

        if self.board.captures[opponent] >= 8:
            return -5 * 10**8  # must block immediately

        my_score = self._evaluate_player(player)
        opp_score = self._evaluate_player(opponent)

        # optional: only enable double-threat later if stable
        threat_bonus = 0
        if len(self.board.moves) > 6:
            threat_bonus = self._double_threat_bonus(player)

        return my_score - 1.2 * opp_score + threat_bonus

    # =========================
    # PLAYER SCORE (INCREMENTAL)
    # =========================

    def _evaluate_player(self, player):
        score = 0

        if not self.board.moves:
            return 0

        # 🔥 Only evaluate around recent moves (performance critical)
        positions = set()

        for (x, y, _, _) in self.board.moves[-6:]:
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 19 and 0 <= ny < 19:
                        positions.add((nx, ny))

        for (x, y) in positions:
            if not self._is_player(x, y, player):
                continue

            for dx, dy in [(1,0), (0,1), (1,1), (1,-1)]:
                score += self._evaluate_direction(x, y, dx, dy, player)

        # capture bonus
        c = self.board.captures[player]

        if c >= 8:
            score += 20000   # super dangerous
        elif c >= 6:
            score += 5000
        else:
            score += c * 800
        # score += self.board.captures[player] * 800

        return score

    # =========================
    # DIRECTION SCAN
    # =========================

    def _evaluate_direction(self, x, y, dx, dy, player):
        count = 1
        open_ends = 0

        # forward
        nx, ny = x + dx, y + dy
        while self._inside(nx, ny):
            if self._is_player(nx, ny, player):
                count += 1
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
                count += 1
                nx -= dx
                ny -= dy
            elif self._is_empty(nx, ny):
                open_ends += 1
                break
            else:
                break

        return self._score_pattern(count, open_ends)

    # =========================
    # PATTERN SCORING
    # =========================

    def _score_pattern(self, count, open_ends):
        if count >= 5:
            return 100000

        if count == 4:
            if open_ends == 2:
                return 10000  # open four
            elif open_ends == 1:
                return 5000   # closed four

        if count == 3:
            if open_ends == 2:
                return 1000   # open three
            elif open_ends == 1:
                return 200

        if count == 2:
            if open_ends == 2:
                return 50

        return 0

    # =========================
    # DOUBLE THREAT BONUS
    # =========================

    def _double_threat_bonus(self, player):
        bonus = 0

        # limit to avoid slowdown
        moves = self.board.get_candidate_moves()[:8]

        for (x, y) in moves:
            if self.board.has_stone(x, y):
                continue
            if not self.board.is_legal_move(x, y, player):
                continue

            self.board.play(x, y, player)

            threes = self._count_open_threes(x, y, player)

            if threes >= 2:
                bonus += 5000

            if self.board.captures[player] >= 10:
                self.board.undo()
                return 10**9  # instant win move

            self.board.undo()

        return bonus

    def _count_open_threes(self, x, y, player):
        count = 0

        for dx, dy in [(1,0), (0,1), (1,1), (1,-1)]:
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

            if stones == 3 and open_ends == 2:
                count += 1

        return count

    # =========================
    # HELPERS
    # =========================

    def _inside(self, x, y):
        return 0 <= x < 19 and 0 <= y < 19

    def _is_empty(self, x, y):
        return not self.board.has_stone(x, y)

    def _is_player(self, x, y, player):
        bit = 1 << (x * 19 + y)
        if player == BLACK:
            return self.board.black_bits & bit
        else:
            return self.board.white_bits & bit
