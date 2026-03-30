import pygame
import math

class GameUI:
    def __init__(self, game):
        self.game = game
        self.CELL_SIZE = 75
        self.BOARD_SIZE = game.BOARD_SIZE
        self.font_large = pygame.font.SysFont(None, self.CELL_SIZE // 2)
        self.WINDOW_SIZE = self.CELL_SIZE * 20

        self.board_pixel = (self.BOARD_SIZE - 1) * self.CELL_SIZE

        self.MARGIN = (self.WINDOW_SIZE - self.board_pixel) // 2

        self.black_stone = create_raytraced_stone(30, True)
        self.white_stone = create_raytraced_stone(30, False)
        self.animations = []
        self.turn = "Your Turn"
        self.player = 1
        self.text_colour = (70, 130, 255) 
        self.running = True
        self.ai_turn = False
        self.ai_thinking = False
        self.just_played = False
        self.winner = None
        self.mode = None
        self.show_rules = False
        self.mouse_pos = (0, 0)
        self.error_message = None
        self.error_time = 0
        self.error_cell = None
        self.ai_menu_open = False
        self.ai_buttons = []
        self.rule = None
        self.frist_turn = True
        self.move_count = 0
        self.last_ai_move = None
        self.hint = False
        self.hint_cell = None
        self.start_rule = None
        self.show_swap = False
        self.is_swap = False
        self.notification = None
        self.notification_timer = 0
        

        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_SIZE, self.WINDOW_SIZE))

    def draw_board(self):
        self.screen.fill((200,170,120))


        for i in range(self.game.BOARD_SIZE):
            offset = i * self.CELL_SIZE

            pygame.draw.line(
                self.screen, (0,0,0),
                (self.MARGIN, self.MARGIN + offset),
                (self.MARGIN + self.board_pixel, self.MARGIN + offset)
            )

            pygame.draw.line(
                self.screen, (0,0,0),
                (self.MARGIN + offset, self.MARGIN),
                (self.MARGIN + offset, self.MARGIN + self.board_pixel)
        )

    def draw_stones(self):
        radius = self.CELL_SIZE // 3
        for x in range(self.game.BOARD_SIZE):
            for y in range(self.game.BOARD_SIZE):
                bit = 1 << (x * self.game.BOARD_SIZE + y)

                if self.game.black & bit or self.game.white & bit:
                    px = self.MARGIN + y * self.CELL_SIZE
                    py = self.MARGIN + x * self.CELL_SIZE

                    is_black = bool(self.game.black & bit)
                    self.draw_stone(px, py, radius, is_black, 1.0, 1.0)

        if self.last_ai_move and not self.ai_turn:
            x, y = self.last_ai_move

            px = self.MARGIN + y * self.CELL_SIZE
            py = self.MARGIN + x * self.CELL_SIZE

            pulse = int(5 * math.sin(pygame.time.get_ticks() * 0.005))
            pygame.draw.circle(self.screen, (255,255,0), (px, py), radius+15 + pulse, 3)
        
        if self.hint and self.hint_cell:
            x, y = self.hint_cell

            px = self.MARGIN + y * self.CELL_SIZE
            py = self.MARGIN + x * self.CELL_SIZE

            radius = self.CELL_SIZE // 3
            if self.is_swap:
                color = (255,255,255,100) if self.player == 1 else (0,0,0,100)
            else:
                color = (0,0,0,100) if self.player == 1 else (255,255,255,100)
            ghost = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(ghost, color, (radius, radius), radius)

            self.screen.blit(ghost, (px-radius, py-radius))
            pulse = int(5 * math.sin(pygame.time.get_ticks() * 0.005))

            pygame.draw.circle(
                self.screen,
                (50, 200, 255),
                (px, py),
                radius + 10 + pulse,
                2
            )
        

    def draw_stone(self, px, py, radius, is_black, scale, reflection):
        r = int(radius * scale)

        shadow_alpha = int(60 * scale)
        shadow = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0,0,0,shadow_alpha), (r,r), r)
        self.screen.blit(shadow, (px - r + 3, py - r + 3))

        stone = self.black_stone if is_black else self.white_stone

        stone_scaled = pygame.transform.smoothscale(stone, (r*2, r*2))
        self.screen.blit(stone_scaled, (px - r, py - r))
        if reflection < 1.0:
            overlay = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.ellipse(
                overlay,
                (255,255,255, int(120 * reflection)),
                (r//4, r//6, r, r//2)
            )
            self.screen.blit(overlay, (px - r, py - r))
        

    def draw_text(self, text, y, color=(0,0,0)):

        center_x = self.WINDOW_SIZE // 2

        turn_text = f"Turn {(self.move_count) // 2 + 1}"
        turn_surf = self.font_large.render(turn_text, True, (255, 215, 0))

        BOX_W = self.CELL_SIZE * 2.5
        BOX_H = self.CELL_SIZE * 0.8

        turn_box = pygame.Rect(0, 0, BOX_W, BOX_H)
        turn_box.center = (center_x - self.CELL_SIZE * 1.3, y)
        turn_rect = turn_surf.get_rect(center=turn_box.center)
        pygame.draw.rect(self.screen, (40,40,50), turn_box, border_radius=8)
        pygame.draw.rect(self.screen, (200,200,200), turn_box, 2, border_radius=8)

        self.screen.blit(turn_surf, turn_rect)

        # ===== TEXT =====
        text_surf = self.font_large.render(text, True, color)

        text_box = pygame.Rect(0, 0, BOX_W, BOX_H)
        text_box.center = (center_x + self.CELL_SIZE * 1.3, y)
        text_rect = text_surf.get_rect(center=text_box.center)
        pygame.draw.rect(self.screen, (30,30,30), text_box, border_radius=10)
        pygame.draw.rect(self.screen, (200,200,200), text_box, 2, border_radius=10)

        self.screen.blit(text_surf, text_rect)

    def draw_error_cell(self):
        if not self.error_cell:
            return

        x, y = self.error_cell

        px = self.MARGIN + y * self.CELL_SIZE
        py = self.MARGIN + x * self.CELL_SIZE

        pygame.draw.circle(self.screen, (255, 80, 80), (px, py), self.CELL_SIZE // 3 + 8, 3)

        size = self.CELL_SIZE // 3
        pygame.draw.line(self.screen, (255,80,80), (px-size, py-size), (px+size, py+size), 3)
        pygame.draw.line(self.screen, (255,80,80), (px+size, py-size), (px-size, py+size), 3)

    def draw_winner(self, text, mouse_pos):
        overlay = pygame.Surface((self.WINDOW_SIZE, self.WINDOW_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        self.screen.blit(overlay, (0, 0))

        center_x = self.WINDOW_SIZE // 2
        center_y = self.WINDOW_SIZE // 2

        font = pygame.font.SysFont(None, 80)
        text_surf = font.render(text, True, (0, 255, 255))
        rect = text_surf.get_rect(center=(center_x, center_y - 120))

        shadow = font.render(text, True, (0,0,0))
        self.screen.blit(shadow, (rect.x+3, rect.y+3))
        self.screen.blit(text_surf, rect)

        spacing = self.CELL_SIZE

        self.btn_restart = self.draw_button(
            "BACK TO MENU",
            center_y,
            mouse_pos,
            fontsize=40,
            width=self.CELL_SIZE * 2.5,
            height=self.CELL_SIZE * 0.8
        )

        self.btn_quit = self.draw_button(
            "QUIT",
            center_y + spacing,
            mouse_pos,
            fontsize=40,
            width=self.CELL_SIZE * 2.5,
            height=self.CELL_SIZE * 0.8
        )

    def draw_menu(self, mouse_pos):
        self.draw_board()
        overlay = pygame.Surface((self.WINDOW_SIZE, self.WINDOW_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        self.screen.blit(overlay, (0, 0))

        center_x = self.WINDOW_SIZE // 2
        center_y = self.WINDOW_SIZE // 2

        font_big = pygame.font.SysFont(None, self.CELL_SIZE)
        title = font_big.render("GOMOKU", True, (240,240,240))
        rect = title.get_rect(center=(center_x, center_y - self.CELL_SIZE * 2))

        shadow = font_big.render("GOMOKU", True, (0,0,0))
        self.screen.blit(shadow, (rect.x+4, rect.y+4))
        self.screen.blit(title, rect)

        spacing = self.CELL_SIZE
        start_y = center_y - self.CELL_SIZE // 2

        self.btn_vs   = self.draw_button("PLAYER vs PLAYER", start_y, mouse_pos)
        self.btn_ai   = self.draw_button("PLAYER vs AI", start_y + spacing, mouse_pos)
        self.btn_rules = self.draw_button("RULES", start_y + spacing * 2, mouse_pos)
        self.btn_quit = self.draw_button("QUIT", start_y + spacing * 3, mouse_pos)
        if self.btn_ai.collidepoint(mouse_pos):
            self.ai_menu_open = True
        if self.btn_vs.collidepoint(mouse_pos) or self.btn_rules.collidepoint(mouse_pos) or self.btn_quit.collidepoint(mouse_pos):
            self.ai_menu_open = False
        if self.ai_menu_open:
            self.draw_ai_menu(start_y + spacing - self.CELL_SIZE * 0.3, mouse_pos)

    def draw_menu_2(self, mouse_pos):
        self.draw_board()
        overlay = pygame.Surface((self.WINDOW_SIZE, self.WINDOW_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        self.screen.blit(overlay, (0, 0))

        center_x = self.WINDOW_SIZE // 2
        center_y = self.WINDOW_SIZE // 2

        font_big = pygame.font.SysFont(None, 100)
        title = font_big.render("GOMOKU", True, (240,240,240))
        rect = title.get_rect(center=(center_x, center_y - 200))

        shadow = font_big.render("GOMOKU", True, (0,0,0))
        self.screen.blit(shadow, (rect.x+4, rect.y+4))
        self.screen.blit(title, rect)

        spacing = self.CELL_SIZE
        start_y = center_y - self.CELL_SIZE // 2

        self.btn_mode1   = self.draw_button("STANDARD", start_y, mouse_pos)
        self.btn_mode2   = self.draw_button("PRO", start_y + spacing, mouse_pos)
        self.btn_mode3 = self.draw_button("SWAP", start_y + spacing * 2, mouse_pos)
        self.btn_back = self.draw_button("BACK", start_y + spacing * 3, mouse_pos)


    def draw_ai_menu(self, ai_y, mouse_pos):
        options = ["EASY", "MEDIUM", "HARD", "EXPERT"]
        self.ai_buttons = []

        center_x = self.WINDOW_SIZE // 2  + (self.WINDOW_SIZE // 6) + 10
        spacing = self.CELL_SIZE // 1.5

        for i, opt in enumerate(options):
            y = ai_y + i * spacing
            rect = pygame.Rect(center_x, y, self.CELL_SIZE * 1.3, self.CELL_SIZE * 0.6)

            hover = rect.collidepoint(mouse_pos)

            color = (120,120,150)  if hover else (60,60,80)
            if hover:
                rect.inflate_ip(10, 6)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            border_color = (255,255,255) if hover  else (180,180,180)
            pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=10)
            font = pygame.font.SysFont(None, self.CELL_SIZE // 3)
            text = font.render(opt, True, (255,255,255))
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

            self.ai_buttons.append((opt, rect))

    def draw_back_button(self, mouse_pos):
        return self.draw_button(text="BACK TO MENU", mouse_pos=mouse_pos, y =(self.WINDOW_SIZE - self.CELL_SIZE * 0.35), height=self.CELL_SIZE * 0.5, width=self.CELL_SIZE * 2.5)


    def draw_button(self, text, y, mouse_pos, fontsize=42, height=None, width=None, bg_color=None, text_color=(255,255,255)): 
        font = pygame.font.SysFont(None, self.CELL_SIZE // 3)

        WIDTH = self.WINDOW_SIZE // 3
        if width:
            WIDTH = width
        HEIGHT = self.CELL_SIZE // 1.5
        if height:
            HEIGHT = height
        

        center_x = self.WINDOW_SIZE // 2

        box_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        box_rect.center = (center_x, y)

        

        box = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        hover = box_rect.collidepoint(mouse_pos)
        if bg_color is None:
            if hover or (self.ai_menu_open and text == "PLAYER vs AI"):
                # box_rect.inflate_ip(self.CELL_SIZE // 10, self.CELL_SIZE * 0.06)
                bg_color = (120, 120, 150, 220)
            else:
                bg_color = (60, 60, 80, 160)
        else:
            hover = None

        pygame.draw.rect(box, bg_color, box.get_rect(), border_radius=14)

        # border
        border_color = (255,255,255) if hover or (self.ai_menu_open and text == "PLAYER vs AI") else (180,180,180)
        pygame.draw.rect(box, border_color, box.get_rect(), 2, border_radius=14)

        self.screen.blit(box, box_rect.topleft)

        # ===== TEXT (center in box) =====
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=box_rect.center)

        # shadow
        shadow = font.render(text, True, (0,0,0))
        self.screen.blit(shadow, (text_rect.x+2, text_rect.y+2))

        self.screen.blit(text_surf, text_rect)

        return box_rect
    
    def draw_rules(self):
        overlay = pygame.Surface((self.WINDOW_SIZE, self.WINDOW_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        box_w, box_h = 700, 500
        box = pygame.Rect(0, 0, box_w, box_h)
        box.center = (self.WINDOW_SIZE//2, self.WINDOW_SIZE//2)

        pygame.draw.rect(self.screen, (40,40,50), box, border_radius=15)
        pygame.draw.rect(self.screen, (200,200,200), box, 2, border_radius=15)

        font_title = pygame.font.SysFont(None, 50)
        font = pygame.font.SysFont(None, 30)

        title = font_title.render("RULES", True, (255,255,255))
        self.screen.blit(title, (box.x + 20, box.y + 20))

        rules = [
            "• Place stones on intersections",
            "• First to get 5 in a row wins",
            "• Capture enemy stones by surrounding",
            "• Horizontal, vertical, diagonal all count",
            "",
            "Press ESC or click to close"
        ]

        y = box.y + 100
        for line in rules:
            text = font.render(line, True, (220,220,220))
            self.screen.blit(text, (box.x + 40, y))
            y += 40
    
    def draw_error(self):
        if not self.error_message or not self.error_cell:
            return

        font = pygame.font.SysFont(None, 28)

        x, y = self.error_cell

        px = self.MARGIN + y * self.CELL_SIZE
        py = self.MARGIN + x * self.CELL_SIZE

        text = font.render(self.error_message, True, (255, 80, 80))

        rect = text.get_rect(center=(px, py + self.CELL_SIZE // 2 + 20))

        if rect.bottom > self.WINDOW_SIZE:
            rect.top = py - self.CELL_SIZE // 2 - 20
        box = rect.inflate(12, 8)
        pygame.draw.rect(self.screen, (30,30,30), box, border_radius=6)

        self.screen.blit(text, rect)

    def draw_score(self, game):
        black_score, white_score = game.board.get_capture_counts()
        font = pygame.font.SysFont(None, self.CELL_SIZE // 3)

        panel_w = self.CELL_SIZE * 1.5
        panel_h = self.CELL_SIZE * 0.6
        margin_y = self.CELL_SIZE // 5

        left_x = self.CELL_SIZE
        right_x = self.WINDOW_SIZE - self.CELL_SIZE - panel_w

        # 🔥 swap logic
        if self.is_swap:
            left_score, right_score = white_score, black_score
            left_player, right_player = -1, 1
            left_color, right_color = (255,255,255), (0,0,0)
        else:
            left_score, right_score = black_score, white_score
            left_player, right_player = 1, -1
            left_color, right_color = (0,0,0), (255,255,255)

        def draw_panel(rect, player, score, stone_color, is_left):
            # background
            pygame.draw.rect(self.screen, (80,80,80), rect, border_radius=10)

            # highlight current player
            if game.current_player == player:
                pygame.draw.rect(self.screen, (200,200,200), rect, 3, border_radius=10)

                glow = pygame.Surface((rect.width+12, rect.height+12), pygame.SRCALPHA)
                pygame.draw.rect(glow, (200,200,200,60), glow.get_rect(), border_radius=12)
                self.screen.blit(glow, (rect.x-6, rect.y-6))

            # stone position
            if is_left:
                stone_pos = (rect.x + self.CELL_SIZE * 0.3, rect.centery)
                text_pos = (rect.x + self.CELL_SIZE * 0.9, rect.centery)
            else:
                stone_pos = (rect.right - self.CELL_SIZE * 0.3, rect.centery)
                text_pos = (rect.right - self.CELL_SIZE * 0.9, rect.centery)

            # draw stone
            pygame.draw.circle(self.screen, stone_color, stone_pos, self.CELL_SIZE * 0.18)

            # draw score
            text = font.render(str(score), True, (255,255,255))
            text_rect = text.get_rect(center=text_pos)
            self.screen.blit(text, text_rect)

        # create rects
        left_rect = pygame.Rect(left_x, margin_y, panel_w, panel_h)
        right_rect = pygame.Rect(right_x, margin_y, panel_w, panel_h)

        # draw both panels
        draw_panel(left_rect, left_player, left_score, left_color, True)
        draw_panel(right_rect, right_player, right_score, right_color, False)

    def draw_center_notification(self, message):
        if not message:
            return

        # font
        font = pygame.font.SysFont(None, 48)

        # render text
        text = font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.WINDOW_SIZE // 2, self.WINDOW_SIZE // 2))

        # background box
        padding_x = 30
        padding_y = 20
        bg_rect = pygame.Rect(
            text_rect.x - padding_x,
            text_rect.y - padding_y,
            text_rect.width + padding_x * 2,
            text_rect.height + padding_y * 2
        )

        # semi-transparent background
        overlay = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect(), border_radius=12)
        self.screen.blit(overlay, (bg_rect.x, bg_rect.y))

        # border
        pygame.draw.rect(self.screen, (200, 200, 200), bg_rect, 2, border_radius=12)

        # glow (optional)
        glow = pygame.Surface((bg_rect.width+20, bg_rect.height+20), pygame.SRCALPHA)
        pygame.draw.rect(glow, (255,255,255,40), glow.get_rect(), border_radius=14)
        self.screen.blit(glow, (bg_rect.x-10, bg_rect.y-10))

        # draw text
        self.screen.blit(text, text_rect)

    def get_cell(self, pos):
        mx, my = pos

        x = int((my - self.MARGIN + self.CELL_SIZE/2) // self.CELL_SIZE)
        y = int((mx - self.MARGIN + self.CELL_SIZE/2) // self.CELL_SIZE)

        if 0 <= x < self.game.BOARD_SIZE and 0 <= y < self.game.BOARD_SIZE:
            return x, y
        return None
    def add_animation(self, x, y, is_black):
        self.animations.append({
            "x": x,
            "y": y,
            "is_black": is_black,
            "time": 0.0
        })
    def reset(self):
        self.animations.clear()
        self.turn = "Your Turn"
        self.text_colour = (70, 130, 255)
        self.ai_turn = False
        self.just_played = False
        self.winner = None
        self.mode = None
        self.show_rules = False
        self.error_message = None
        self.error_time = 0
        self.error_cell = None
        self.ai_menu_open = False
        self.rule = None
        self.start_rule = None
        self.frist_turn = True
        self.move_count = 0
        self.last_ai_move = None
        self.hint = False
        self.hint_cell = None
        self.show_swap = False
        self.is_swap = False
        self.notification = None
        self.notification_timer = 0
    
import pygame
import math

def create_raytraced_stone(radius, is_black):
    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    light_dir = (-0.5, -0.5, 1)  # ทิศแสง
    length = math.sqrt(sum(i*i for i in light_dir))
    light_dir = tuple(i/length for i in light_dir)

    for y in range(size):
        for x in range(size):
            nx = (x - radius) / radius
            ny = (y - radius) / radius
            dist = nx*nx + ny*ny

            if dist > 1:
                continue

            nz = math.sqrt(1 - dist)
            normal = (nx, ny, nz)

            dot = max(0, sum(normal[i]*light_dir[i] for i in range(3)))

            reflect = (
                2 * dot * normal[0] - light_dir[0],
                2 * dot * normal[1] - light_dir[1],
                2 * dot * normal[2] - light_dir[2],
            )
            spec = max(reflect[2], 0) ** 20

            if is_black:
                base = 5
                ambient = 0.15
                dot = ambient + (1 - ambient) * dot
                diffuse = dot * 0.6

                specular = spec * 1.0

                r = int(base + 80 * diffuse + 200 * specular)
                g = int(base + 80 * diffuse + 200 * specular)
                b = int(base + 100 * diffuse + 255 * specular)
            else:
                base = 180
                ambient = 0.15
                dot = ambient + (1 - ambient) * dot
                diffuse = dot * 0.6

                specular = spec * 0.09

                r = int(base + 80 * diffuse + 200 * specular)
                g = int(base + 80 * diffuse + 200 * specular)
                b = int(base + 100 * diffuse + 255 * specular)

            surf.set_at((x, y), (min(r,255), min(g,255), min(b,255), 255))

    return surf

