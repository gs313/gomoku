from board import BLACK, WHITE

MAX_MOVES = 12
class MoveGenerator:
    def __init__(self, board):
        self.board = board

    # =========================
    # MAIN ENTRY
    # =========================

    def generate(self, player):
        moves = self.board.get_candidate_moves()

        scored = []

        for (x, y) in moves:
            score = self._score_move(x, y, player)
            scored.append(((x, y), score))

        # sort descending
        scored.sort(key=lambda x: x[1], reverse=True)

        return [move for (move, _) in scored[MAX_MOVES:]]

    # =========================
    # SCORING FUNCTION
    # =========================

    def _score_move(self, x, y, player):
        score = 0

        # center preference
        cx, cy = 9, 9
        score -= abs(x - cx) + abs(y - cy)

        # neighbor density
        score += self._count_neighbors(x, y) * 10

        # alignment potential
        score += self._line_potential(x, y, player)

        return score

    # =========================
    # NEIGHBOR COUNT
    # =========================

    def _count_neighbors(self, x, y):
        count = 0

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue

                nx, ny = x + dx, y + dy

                if 0 <= nx < 19 and 0 <= ny < 19:
                    if self.board.has_stone(nx, ny):
                        count += 1

        return count

    # =========================
    # LINE POTENTIAL
    # =========================

    def _line_potential(self, x, y, player):
        score = 0

        directions = [(1,0), (0,1), (1,1), (1,-1)]

        for dx, dy in directions:
            count = 1  # include current move

            # forward
            nx, ny = x + dx, y + dy
            while 0 <= nx < 19 and 0 <= ny < 19:
                if self.board.has_stone(nx, ny):
                    if self._is_player(nx, ny, player):
                        count += 1
                        nx += dx
                        ny += dy
                    else:
                        break
                else:
                    break

            # backward
            nx, ny = x - dx, y - dy
            while 0 <= nx < 19 and 0 <= ny < 19:
                if self.board.has_stone(nx, ny):
                    if self._is_player(nx, ny, player):
                        count += 1
                        nx -= dx
                        ny -= dy
                    else:
                        break
                else:
                    break

            score += count * count  # quadratic weight

        return score

    def _is_player(self, x, y, player):
        bit = 1 << (x * 19 + y)
        if player == BLACK:
            return self.board.black_bits & bit
        else:
            return self.board.white_bits & bit
