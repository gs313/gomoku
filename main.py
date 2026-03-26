import pygame
from gamestate import GameState
from gamegui import GameUI
from minimax import MinimaxAI

if __name__ == "__main__":
    game = GameState()
    ui = GameUI(game)
    ai = MinimaxAI(game.board, max_depth=4)

    running = True
    ai_turn = False
    ai_thinking = False

    while running:

        # =========================
        # EVENT LOOP
        # =========================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ai_turn or ai_thinking:
                    continue

                cell = ui.get_cell(pygame.mouse.get_pos())

                if cell and game.put(*cell):
                    print("Human:", cell)

                    ui.draw_board()
                    ui.draw_stones()
                    pygame.display.flip()

                    ai_turn = True

        # =========================
        # AI TURN
        # =========================
        if ai_turn:
            ai_thinking = True

            ai_move = ai.find_best_move(game.current_player)

            if ai_move:
                game.put(*ai_move)
                print("AI:", ai_move)

            ai_turn = False
            ai_thinking = False

        # =========================
        # RENDER
        # =========================
        ui.draw_board()
        ui.draw_stones()
        pygame.display.flip()
