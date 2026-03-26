from gamestate import GameState
from gamegui import GameUI
import pygame

if __name__ == "__main__":
    game = GameState()
    ui = GameUI(game)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                cell = ui.get_cell(pygame.mouse.get_pos())
                if cell:
                    game.put(*cell)
                    print(*cell)

        ui.draw_board()
        ui.draw_stones()
        pygame.display.flip()