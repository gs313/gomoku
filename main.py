import pygame
from gamestate import GameState
from gamegui import GameUI
from minimax import MinimaxAI


def check_win(game, ui):
    if game.board.check_win(1):
        ui.ai_turn = False
        ui.winner = "Black Wins!"
        ui.draw_winner(ui.winner)
    if game.board.check_win(-1):
        ui.ai_turn = False
        ui.winner = "White Wins!"
        ui.draw_winner(ui.winner)

def update_cursor(ui, mouse_pos):
    if (ui.btn_vs.collidepoint(mouse_pos) or
        ui.btn_ai.collidepoint(mouse_pos) or
        ui.btn_quit.collidepoint(mouse_pos)):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

def set_mode(ui):
    mouse_pos = pygame.mouse.get_pos()
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ui.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if ui.btn_vs.collidepoint(mouse_pos):
                ui.mode = "vs"
            elif ui.btn_ai.collidepoint(mouse_pos):
                ui.mode = "ai"
            elif ui.btn_quit.collidepoint(mouse_pos):
                ui.mode = "quit"
                ui.running = False
    ui.draw_menu(mouse_pos)
    pygame.display.flip()
    update_cursor(ui, mouse_pos)

def play_turn(ui, game):
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ui.running = False
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                ui.running = False
                break
            elif event.key == pygame.K_r and ui.winner:
                game = GameState()
                ui = GameUI(game)
                ui.winner = None
                ui.mode = None
            elif event.key == pygame.K_q and ui.winner:
                ui.running = False
                break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if ui.winner or ui.ai_thinking or ui.winner:
                continue
            
            cell = ui.get_cell(pygame.mouse.get_pos())
            if cell and game.put(*cell):
                if ui.mode == "vs":
                    if ui.player == 1:
                        ui.player = 2
                        ui.turn = f"Player {ui.player} turn"
                        ui.text_colour = (240, 240, 240)
                    else:
                        ui.player = 1
                        ui.turn = f"Player {ui.player} Turn"
                        ui.text_colour = (70, 130, 255) 
                else:
                    ui.turn = "AI Turn"
                    ui.ai_turn = True
                    ui.text_colour = (255, 80, 80)
                    ui.just_played = True

def ai_turn(ui, game):
    if ui.just_played:
        ui.just_played = False
    else:
        ui.ai_thinking = True
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAIT)
        ai_move = ai.find_best_move(game.current_player)
        if ai_move:
            game.put(*ai_move)
            print("AI:", ai_move)
            ui.ai_turn = False
            ui.ai_thinking = False
            ui.turn = "Your Turn"
            ui.text_colour = (70, 130, 255)
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            pygame.event.clear(pygame.MOUSEBUTTONDOWN)

if __name__ == "__main__":

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("Gomoku")
    clock = pygame.time.Clock()
    game = GameState()
    ui = GameUI(game)
    ai = MinimaxAI(game.board, max_depth=20,time_limit=1)
    
    while ui.running:
        if ui.mode is None:
            set_mode(ui)
            continue
        play_turn(ui, game)
        if ui.ai_turn and ui.running :
            ai_turn(ui, game)
        
        ui.draw_board()
        ui.draw_stones()
        ui.draw_text(ui.turn, 50, ui.text_colour)
        ui.draw_score(game)
        if ui.running:
            check_win(game, ui)
        pygame.display.flip()
