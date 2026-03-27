import pygame
from gamestate import GameState
from gamegui import GameUI
from minimax import MinimaxAI
import argparse


def check_win(game):
    if game.board.check_win(1):
        return "Black Wins!"
    if game.board.check_win(-1):
        return "White Wins!"
    return None

def update_cursor(ui, mouse_pos):
    if (ui.btn_vs.collidepoint(mouse_pos) or
        ui.btn_ai.collidepoint(mouse_pos) or
        ui.btn_quit.collidepoint(mouse_pos)):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

def set_mode(running, mode):
    mouse_pos = pygame.mouse.get_pos()
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if ui.btn_vs.collidepoint(mouse_pos):
                mode = "vs"
            elif ui.btn_ai.collidepoint(mouse_pos):
                mode = "ai"
            elif ui.btn_quit.collidepoint(mouse_pos):
                mode = "quit"
                running = False
    ui.draw_menu(mouse_pos)
    pygame.display.flip()
    update_cursor(ui, mouse_pos)
    return mode, running

if __name__ == "__main__":

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("Gomoku")
    clock = pygame.time.Clock()

    turn = "Your Turn"
    player = 1
    text_colour = (70, 130, 255) 

    game = GameState()
    ui = GameUI(game)
    ai = MinimaxAI(game.board, max_depth=20,time_limit=1)
    ui.draw_board()
    ui.draw_text(turn, 50, text_colour)
    pygame.display.flip()

    running = True
    ai_turn = False
    ai_thinking = False
    just_played = False
    winner = None
    mode = None
    
    while running:
        if mode is None:
            mode, running = set_mode(running, mode)
            continue
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                elif event.key == pygame.K_r and winner:
                    game = GameState()
                    ui = GameUI(game)
                    winner = None
                    mode = None
                elif event.key == pygame.K_q and winner:
                    running = False
                    break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ai_turn or ai_thinking or winner:
                    continue
                

                cell = ui.get_cell(pygame.mouse.get_pos())

                if cell and game.put(*cell):
                    if mode == "vs":
                        if player == 1:
                            player = 2
                            turn = f"Player {player} Turn"
                            text_colour = (240, 240, 240)
                        else:
                            player = 1
                            turn = f"Player {player} Turn"
                            text_colour = (70, 130, 255) 
                    else:
                        turn = "AI Turn"
                        ai_turn = True
                        text_colour = (255, 80, 80)
                        just_played = True

        if ai_turn and running :
            if just_played:
                just_played = False
            else:
                ai_thinking = True
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAIT)

                ai_move = ai.find_best_move(game.current_player)

                if ai_move:
                    game.put(*ai_move)
                    print("AI:", ai_move)
                    ai_turn = False
                    ai_thinking = False
                    turn = "Yout Turn"
                    text_colour = (70, 130, 255)
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    pygame.event.clear(pygame.MOUSEBUTTONDOWN)
        
        ui.draw_board()
        ui.draw_stones()
        ui.draw_text(turn, 50, text_colour)
        if running:
            winner = check_win(game)
            if winner:
                ai_turn = False
                ui.draw_winner(winner)
        pygame.display.flip()
        
                

        

        
        
