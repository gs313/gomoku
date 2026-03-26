import pygame
from gamestate import GameState
from gamegui import GameUI
from minimax import MinimaxAI

if __name__ == "__main__":
    pygame.init()
    clock = pygame.time.Clock()
    game = GameState()
    ui = GameUI(game)
    ai = MinimaxAI(game.board, max_depth=20,time_limit=1)
    ui.draw_board()
    pygame.display.flip()

    running = True
    ai_turn = False
    ai_thinking = False

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ai_turn or ai_thinking:
                    continue

                cell = ui.get_cell(pygame.mouse.get_pos())

                if cell and game.put(*cell):
                    print("Human:", cell)
                    ai_turn = True
                    ui.draw_board()
                    ui.draw_stones()
                    pygame.display.flip()
                    if game.board.check_win(1):
                        print("Black wins!")
                        running = False

        if ai_turn and running:
            ai_thinking = True

            ai_move = ai.find_best_move(game.current_player)

            if ai_move:
                game.put(*ai_move)
                print("AI:", ai_move)
                ui.draw_board()
                ui.draw_stones()
                pygame.display.flip()
                if game.board.check_win(-1):
                    print("White wins!")
                    running = False

            ai_turn = False
            ai_thinking = False
            pygame.event.clear(pygame.MOUSEBUTTONDOWN)

        

        
        
