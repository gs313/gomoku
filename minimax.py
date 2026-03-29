from heuristic import Heuristic
from move_generator import MoveGenerator
import time

INF = 10**12


class MinimaxAI:
    def __init__(self, board, max_depth=6, time_limit=None):
        self.board = board
        self.max_depth = max_depth
        self.time_limit = time_limit

        self.nodes = 0
        self.depth_reached = 0
        self.last_completed_depth = 0

        self.heuristic = Heuristic(board)
        self.move_gen = MoveGenerator(board)

        self.killer_moves = {}

        self.tt = {}

    # =========================
    # ENTRY POINT
    # =========================

    def find_best_move(self, player):
        self.tt.clear()  # 🔥 reset cache

        self.start_time = time.time()
        self.stop = False

        self.nodes = 0
        self.depth_reached = 0
        self.last_completed_depth = 0
        best_move = None

        for depth in range(1, self.max_depth + 1):
            score, move = self._search_root(player, depth, best_move)

            if self.stop:
                break
            if not self.stop:
                self.last_completed_depth = depth
            if move is not None:
                best_move = move
        self.depth_reached = self.last_completed_depth

        self._print_search_stats()

        return best_move

    def _print_search_stats(self):
        elapsed = time.time() - self.start_time

        print("\n=== AI SEARCH STATS ===")
        print(f"Time: {elapsed:.3f}s")
        print(f"Nodes searched: {self.nodes}")
        print(f"Effective depth: {self.depth_reached}")

        if elapsed > 0:
            print(f"Nodes/sec: {int(self.nodes / elapsed)}")

        print("========================\n")

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

        # moves = self.move_gen.generate(player)
        # print(len(moves))
        moves = self._get_moves(player, depth)
        # moves = moves[:20]

        #  move ordering from previous iteration
        if prev_best in moves:
            moves.remove(prev_best)
            moves.insert(0, prev_best)

        for move in moves:
            if self.stop:
                break
            x, y = move

            self.board.play_fast(x, y, player)
            # if not self.board.play(x, y, player):
            #     continue
            # if not self.board.is_legal_move(x, y, player):
            #     continue
            # self.board.play(x, y, player)
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
        self.nodes += 1
        # ⏱️ TIME CHECK
        if self._time_exceeded():
            self.stop = True
            return self.heuristic.evaluate(root_player)
            # return 0
        key = (self._hash(), depth, maximizing, player)

        if key in self.tt:
            return self.tt[key]

        # terminal
        if depth == 0 or self.board.check_win(root_player, fast=True) or self.board.check_win(-root_player, fast = True):
            val = self.heuristic.evaluate(root_player)
            self.tt[key] = val
            return val

        # moves = self.move_gen.generate(player)
        # limit = 4 if depth >= 6 else 8
        # moves = moves[:limit]
        moves = self._get_moves(player, depth)
        killer = self.killer_moves.get(depth)
        if killer in moves:
            moves.remove(killer)
            moves.insert(0, killer)

        if not moves:
            return self.heuristic.evaluate(root_player)

        if not moves:
            return self.heuristic.evaluate(root_player)

        if maximizing:
            value = -INF

            for i, move in enumerate(moves):
                x, y = move

                if not self.board.play_fast(x, y, player):
                    continue

                if i == 0:
                    score = self._alphabeta(
                        depth-1,
                        alpha,
                        beta,
                        -player,
                        False,
                        root_player
                    )
                else:
                    score = self._alphabeta(
                        depth-1,
                        alpha,
                        alpha + 1,
                        -player,
                        False,
                        root_player
                    )

                    if score > alpha:
                        score = self._alphabeta(
                            depth-1,
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
            # for move in moves:
            #     if self.stop:
            #         break
            #     x, y = move

            #     if not self.board.play(x, y, player):
            #         continue
            #     # if not self.board.is_legal_move(x, y, player):
            #     #     continue
            #     # self.board.play(x, y, player)

            #     score = self._alphabeta(
            #         depth - 1,
            #         alpha,
            #         beta,
            #         -player,
            #         False,
            #         root_player
            #     )

            #     self.board.undo()

            #     value = max(value, score)
            #     alpha = max(alpha, value)

            #     if alpha >= beta:
            #         self.killer_moves[depth] = move
            #         break

        else:
            value = INF

            for move in moves:
                if self.stop:
                    break
                x, y = move

                if not self.board.play_fast(x, y, player):
                    continue
                # if not self.board.is_legal_move(x, y, player):
                #     continue
                # self.board.play(x, y, player)

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
                    self.killer_moves[depth] = move
                    break

        self.tt[key] = value
        return value


    def _get_moves(self, player, depth):
        #  1. forced moves first
        # forced = self._get_forced_moves(player)
        # if forced:
        #     return forced

        #  2. adaptive pruning
        moves = self.move_gen.generate(player)
        # print(len(moves))
        # return moves
        # if depth >= 10:
        #     return moves[:2]
        # elif depth >= 8:
        #     return moves[:3]
        if depth >= 6:
            return moves[:3]
        elif depth >= 4:
            return moves[:6]
        else:
            return moves[:10]

    # def _get_forced_moves(self, player):
    #     opponent = -player
    #     winning_moves = []
    #     blocking_moves = []

    #     for (x, y) in self.board.get_candidate_moves():
    #         if not self.board.is_legal_move(x, y, player):
    #             continue

    #         # 🏆 immediate win
    #         if self.board.play(x, y, player):
    #             if self.board.check_win(player):
    #                 self.board.undo()
    #                 return [(x, y)]
    #             self.board.undo()

    #         # 🛑 block opponent win
    #         if self.board.play(x, y, opponent):
    #             if self.board.check_win(opponent, fast=True):
    #                 blocking_moves.append((x, y))
    #             self.board.undo()

    #     if blocking_moves:
    #         return blocking_moves

    #     return []

    def _get_forced_moves(self, player):
        opponent = -player
        moves = self.board.get_candidate_moves()

        # 🏆 1. Immediate winning move
        for (x, y) in moves:
            if not self.board.play(x, y, player):
                continue
            # if not self.board.is_legal_move(x, y, player):
            #     continue

            # self.board.play(x, y, player)
            if self.board.check_win(player, fast=True):
                self.board.undo()
                return [(x, y)]
            self.board.undo()

        # 🚨 2. Are we currently losing?
        opponent_winning = False

        for (x, y) in moves:
            if not self.board.play(x, y, player):
                continue

            # if not self.board.is_legal_move(x, y, opponent):
            #     continue

            # self.board.play(x, y, opponent)
            if self.board.check_win(opponent, fast=True):
                opponent_winning = True
                self.board.undo()
                break
            self.board.undo()

        # 👉 If not losing, no forced moves
        if not opponent_winning:
            return []

        # 🛑 3. Find moves that prevent loss (including capture defense)
        blocking = []

        for (x, y) in moves:
            if not self.board.play(x, y, player):
                continue
            # if not self.board.is_legal_move(x, y, player):
            #     continue

            # self.board.play(x, y, player)

            still_loses = False

            # check if opponent STILL has a winning move
            for (ox, oy) in self.board.get_candidate_moves():
                if not self.board.play(x, y, player):
                    continue
                # if not self.board.is_legal_move(ox, oy, opponent):
                #     continue

                # self.board.play(ox, oy, opponent)

                if self.board.check_win(opponent, fast=True):
                    still_loses = True
                    self.board.undo()
                    break

                self.board.undo()

            self.board.undo()

            if not still_loses:
                blocking.append((x, y))

        if blocking:
            return blocking[:3]

        return []
