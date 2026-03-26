import pygame

class GameUI:
    def __init__(self, game):
        self.game = game
        self.CELL_SIZE = 100
        self.BOARD_SIZE = game.BOARD_SIZE
        self.font_large = pygame.font.SysFont(None, 40)
        self.WINDOW_SIZE = self.CELL_SIZE * 20

        self.board_pixel = (self.BOARD_SIZE - 1) * self.CELL_SIZE

        self.MARGIN = (self.WINDOW_SIZE - self.board_pixel) // 2

        self.black_stone = create_raytraced_stone(30, True)
        self.white_stone = create_raytraced_stone(30, False)
        self.animations = []

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

        text_surf = self.font_large.render(text, True, color)
        text_rect = text_surf.get_rect(center=(self.WINDOW_SIZE//2, y))

        padding = 20
        box_rect = text_rect.inflate(padding*2, padding)

        pygame.draw.rect(self.screen, (30, 30, 30), box_rect, border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), box_rect, 2, border_radius=10)

        shadow = self.font_large.render(text, True, (0, 0, 0))
        self.screen.blit(shadow, (text_rect.x+2, text_rect.y+2))
        self.screen.blit(text_surf, text_rect)

    def draw_winner(self, text):
        overlay = pygame.Surface((self.WINDOW_SIZE, self.WINDOW_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont(None, 80)
        text_surf = font.render(text, True, (0, 255, 255))
        rect = text_surf.get_rect(center=(self.WINDOW_SIZE//2, self.WINDOW_SIZE//2))

        shadow = font.render(text, True, (200,200,200))
        self.screen.blit(shadow, (rect.x+3, rect.y+3))

        small = pygame.font.SysFont(None, 36)
        hint = small.render("Press R to Restart", True, (200,200,200))
        hint_rect = hint.get_rect(center=(self.WINDOW_SIZE//2, self.WINDOW_SIZE//2 + 80))
        self.screen.blit(hint, hint_rect)
        hint2 = small.render("Press Q to Quit", True, (200,200,200))
        hint_rect2 = hint2.get_rect(center=(self.WINDOW_SIZE//2, self.WINDOW_SIZE//2 + 150))
        self.screen.blit(hint2, hint_rect2)

    def draw_menu(self, mouse_pos):
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

        spacing = 120
        start_y = center_y - 40

        self.btn_vs   = self.draw_button("PLAYER vs PLAYER", start_y, mouse_pos)
        self.btn_ai   = self.draw_button("PLAYER vs AI", start_y + spacing, mouse_pos)
        self.btn_quit = self.draw_button("QUIT", start_y + spacing * 2, mouse_pos)

    def draw_button(self, text, y, mouse_pos):
        font = pygame.font.SysFont(None, 42)

        WIDTH = self.WINDOW_SIZE // 3
        HEIGHT = 70

        center_x = self.WINDOW_SIZE // 2

        box_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        box_rect.center = (center_x, y)

        hover = box_rect.collidepoint(mouse_pos)

        box = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        if hover:
            box_rect.inflate_ip(10, 6)
            bg_color = (120, 120, 150, 220)
        else:
            bg_color = (60, 60, 80, 160)

        pygame.draw.rect(box, bg_color, box.get_rect(), border_radius=14)

        # border
        border_color = (255,255,255) if hover else (180,180,180)
        pygame.draw.rect(box, border_color, box.get_rect(), 2, border_radius=14)

        self.screen.blit(box, box_rect.topleft)

        # ===== TEXT (center in box) =====
        text_surf = font.render(text, True, (255,255,255))
        text_rect = text_surf.get_rect(center=box_rect.center)

        # shadow
        shadow = font.render(text, True, (0,0,0))
        self.screen.blit(shadow, (text_rect.x+2, text_rect.y+2))

        self.screen.blit(text_surf, text_rect)

        return box_rect

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

