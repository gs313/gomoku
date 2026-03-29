import pygame
from gamestate import GameState
from gamegui import GameUI
from minimax import MinimaxAI


def check_win(game, ui):
    if game.board.check_win(1):
        ui.ai_turn = False
        ui.winner = "Black Wins!"
    if game.board.check_win(-1):
        ui.ai_turn = False
        ui.winner = "White Wins!"

def update_cursor(ui, mouse_pos):
    if (ui.btn_vs.collidepoint(mouse_pos) or
        ui.btn_ai.collidepoint(mouse_pos) or
        ui.btn_quit.collidepoint(mouse_pos)):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

def set_mode(ui, ai):
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ui.running = False
            continue
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if ui.show_rules:
                ui.show_rules = False
                continue
            if ui.btn_vs.collidepoint(mouse_pos):
                ui.mode = "vs"
                ui.ai_turn = False
            elif ui.btn_rules.collidepoint(mouse_pos):
                ui.show_rules = True
            elif ui.btn_quit.collidepoint(mouse_pos):
                ui.mode = "quit"
                ui.running = False
            if ui.ai_menu_open:
                for mode, rect in ui.ai_buttons:
                    if rect.collidepoint(mouse_pos):
                        ui.mode = "ai"
                        ui.ai_level = mode.lower()
                        ui.ai_menu_open = False
                        print(ui.ai_level)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                if ui.show_rules:
                    ui.show_rules = False
    if ui.winner is None:
        ui.draw_menu(mouse_pos)
        if ui.show_rules:
            ui.draw_rules()
        pygame.display.flip()
        update_cursor(ui, mouse_pos)

def set_game(ui, ai):
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ui.running = False
            continue
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if ui.show_rules:
                ui.show_rules = False
                continue
            if ui.btn_mode1.collidepoint(mouse_pos):
                ui.rule = "standard"
            elif ui.btn_mode2.collidepoint(mouse_pos):
                ui.rule = "pro"
            elif ui.btn_mode3.collidepoint(mouse_pos):
                ui.rule = "swap"
            elif ui.btn_back.collidepoint(mouse_pos):
                ui.mode = None
                break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                if ui.show_rules:
                    ui.show_rules = False
    ui.draw_menu_2(mouse_pos)
    if ui.show_rules:
        ui.draw_rules()
    pygame.display.flip()
    update_cursor(ui, mouse_pos)

def play_turn(ui, game, ai):
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ui.running = False
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                ui.running = False
                break
            if event.key == pygame.K_h and not ui.hint:
                ai_move = ai.find_best_move(game.current_player)
                if ai_move:
                    ui.hint_cell = ai_move
                    ui.hint = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if ui.btn_menu.collidepoint(mouse_pos):
                game.reset()
                ui.reset()
                break
            elif ui.show_swap and ui.btn_swap.collidepoint(mouse_pos):
                print("Player chose to swap")
                ui.is_swap = True
                ui.show_swap = False
                if ui.player == 1:
                    ui.player = 2
                else:                    
                    ui.player = 1
                ui.turn = f"Player {ui.player} turn"
                ui.rule = "standard"
                pygame.event.clear(pygame.MOUSEBUTTONDOWN)
                break
            elif ui.show_swap and ui.btn_play.collidepoint(mouse_pos):
                print("Player chose to play")
                ui.show_swap = False
                ui.rule = "standard"
                pygame.event.clear(pygame.MOUSEBUTTONDOWN)
                break
            if ui.winner or ui.ai_thinking or ui.show_swap:
                continue
            cell = ui.get_cell(pygame.mouse.get_pos())
            if cell:
                ui.hint = False
                if game.put(*cell):
                    if ui.mode == "vs":
                        if (ui.move_count == 0 or ui.move_count == 2) and ui.rule == "pro":
                            is_legal, message = game.is_legal_rule(*cell, ui.move_count, ui.rule)
                            if not is_legal:
                                game.undo()
                                ui.error_message = message
                                ui.error_cell = cell
                                ui.error_time = 1
                                continue
                        if ui.player == 1:
                            ui.player = 2
                            if ui.rule == "swap" and ui.move_count < 2:
                                ui.player = 1
                            ui.turn = f"Player {ui.player} turn"
                            ui.text_colour = (240, 240, 240)
                            ui.move_count = ui.move_count + 1
                        else:
                            ui.player = 1
                            ui.turn = f"Player {ui.player} Turn"
                            ui.text_colour = (70, 130, 255)
                            ui.move_count = ui.move_count + 1
                    else:
                        ui.turn = "AI Turn"
                        ui.ai_turn = True
                        if ui.rule == "swap" and ui.move_count < 3:
                            ui.turn = "Your Turn"
                            ui.ai_turn = False
                        ui.text_colour = (255, 80, 80)
                        ui.just_played = True
                        ui.move_count = ui.move_count + 1
                else:
                    ui.error_message = "Invalid move (Double Three or have stone)"
                    ui.error_cell = cell
                    ui.error_time = 0.7
    if ui.rule == "swap" and ui.move_count == 3:
        ui.player = 2
        ui.show_swap = True
        ui.turn = f"Player {ui.player} Turn"
        ui.text_colour = (70, 130, 255)
    return ui, game, ai

def ai_turn(ui, game, ai):
    if ui.just_played:
        ui.just_played = False
    else:
        ui.ai_thinking = True
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAIT)
        ai_move = ai.find_best_move(game.current_player)
        if ai_move:
            game.put(*ai_move)
            ui.last_ai_move = ai_move
            print("AI:", ai_move)
            ui.ai_turn = False
            ui.ai_thinking = False
            ui.turn = "Your Turn"
            ui.text_colour = (70, 130, 255)
            ui.move_count = ui.move_count + 1
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
        dt = clock.tick(60) / 1000.0
        if ui.error_time > 0:
            ui.error_time -= dt
            if ui.error_time <= 0:
                ui.error_message = None
                ui.error_cell = None
            continue
        if ui.mode is None:
            set_mode(ui, ai)
            ui.move_count = 0
            if ui.mode == "ai":
                ui.ai_turn = False
                ui.turn = "AI Turn"
                ui.text_colour = (255, 80, 80)
                if ui.ai_level == "easy":
                    ai = MinimaxAI(game.board, max_depth=2, time_limit=0.2)
                elif ui.ai_level == "medium":
                    ai = MinimaxAI(game.board, max_depth=6, time_limit=0.5)
                elif ui.ai_level == "hard":
                    ai = MinimaxAI(game.board, max_depth=12, time_limit=0.5)
                else:
                    ai = MinimaxAI(game.board, max_depth=20, time_limit=0.5)
            continue
        if ui.mode is None:
            continue
        if ui.rule is None:
            ui.frist_turn = True
            set_game(ui, ai)
            continue
        
        if ui.ai_turn and ui.running and not ui.winner:
            if ui.frist_turn:
                ui.frist_turn = False
            else:
                ai_turn(ui, game, ai)
        elif not ui.winner:
            if ui.frist_turn:
                ui.frist_turn = False
            ui, game, ai = play_turn(ui, game, ai)
            
        
        ui.draw_board()
        ui.draw_stones()
        ui.draw_text(ui.turn, 50, ui.text_colour)
        ui.draw_score(game)
        ui.draw_error()
        ui.draw_error_cell()
        mouse_pos = pygame.mouse.get_pos()
        if ui.show_swap:
            start_y = ui.CELL_SIZE * 4
            space = ui.CELL_SIZE
            ui.draw_button("Swap or Play?", start_y, mouse_pos, bg_color=(0,0,0), text_color=(70, 130, 255))
            ui.btn_swap = ui.draw_button("SWAP", start_y + space, mouse_pos)
            ui.btn_play = ui.draw_button("PLAY", start_y + space * 2, mouse_pos)
        if not ui.winner:
            ui.btn_menu = ui.draw_back_button(mouse_pos)
            check_win(game, ui)
        else:
            ui.draw_winner(ui.winner, mouse_pos)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if ui.btn_restart.collidepoint(mouse_pos):
                        game.reset()
                        ui.reset()
                        break
                    elif ui.btn_quit.collidepoint(mouse_pos):
                        ui.winner = None
                        ui.running = False
        pygame.display.flip()
        
        
