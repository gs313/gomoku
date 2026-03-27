from heuristic import Heuristic
from move_generator import MoveGenerator
import time

INF = 10**12


class MinimaxAI:
    def __init__(self, board, max_depth=6, time_limit=None):
        self.board = board
        self.max_depth = max_depth
        self.time_limit = time_limit

        self.heuristic = Heuristic(board)
        self.move_gen = MoveGenerator(board)

        self.tt = {}

    # =========================
    # ENTRY POINT
    # =========================

    def find_best_move(self, player):
        self.tt.clear()  # 🔥 reset cache

        self.start_time = time.time()
        self.stop = False

        best_move = None

        for depth in range(1, self.max_depth + 1):
            score, move = self._search_root(player, depth, best_move)

            if move is not None:
                best_move = move

        return best_move

    def _time_exceeded(self):
        if self.time_limit is None:
            return False

        return (time.time() - self.start_time) >= self.time_limit
    # =========================
    # ROOT SEARCH
    # =========================

    def _search_root(self, player, depth, prev_best):
        best_score = -INF
        best_move = None

        moves = self.move_gen.generate(player)
        moves = moves[:12]

        # 🔥 move ordering from previous iteration
        if prev_best in moves:
            moves.remove(prev_best)
            moves.insert(0, prev_best)

        for move in moves:
            x, y = move

            # if not self.board.play(x, y, player):
            #     continue
            if not self.board.is_legal_move(x, y, player):
                continue
            self.board.play(x, y, player)
            score = self._alphabeta(
                depth - 1,
                -INF,
                INF,
                -player,
                False,
                player
            )

            self.board.undo()

            if score > best_score:
                best_score = score
                best_move = move

        return best_score, best_move

    # =========================
    # HASH
    # =========================

    def _hash(self):
        return (self.board.black_bits, self.board.white_bits)

    # =========================
    # ALPHA-BETA
    # =========================

    def _alphabeta(self, depth, alpha, beta, player, maximizing, root_player):
        # ⏱️ TIME CHECK
        if self._time_exceeded():
            self.stop = True
            return self.heuristic.evaluate(root_player)
        key = (self._hash(), depth, maximizing, player)

        if key in self.tt:
            return self.tt[key]

        # terminal
        if depth == 0 or self.board.check_win(root_player) or self.board.check_win(-root_player):
            val = self.heuristic.evaluate(root_player)
            self.tt[key] = val
            return val

        moves = self.move_gen.generate(player)
        moves = moves[:12]

        if not moves:
            return self.heuristic.evaluate(root_player)

        if maximizing:
            value = -INF

            for move in moves:
                x, y = move

                # if not self.board.play(x, y, player):
                #     continue
                if not self.board.is_legal_move(x, y, player):
                    continue
                self.board.play(x, y, player)

                score = self._alphabeta(
                    depth - 1,
                    alpha,
                    beta,
                    -player,
                    False,
                    root_player
                )

                self.board.undo()

                value = max(value, score)
                alpha = max(alpha, value)

                if alpha >= beta:
                    break

        else:
            value = INF

            for move in moves:
                x, y = move

                # if not self.board.play(x, y, player):
                #     continue
                if not self.board.is_legal_move(x, y, player):
                    continue
                self.board.play(x, y, player)

                score = self._alphabeta(
                    depth - 1,
                    alpha,
                    beta,
                    -player,
                    True,
                    root_player
                )

                self.board.undo()

                value = min(value, score)
                beta = min(beta, value)

                if beta <= alpha:
                    break

        self.tt[key] = value
        return value
