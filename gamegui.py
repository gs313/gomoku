import pygame

class GameUI:
    def __init__(self, game):
        self.game = game
        self.CELL_SIZE = 100
        self.BOARD_SIZE = game.BOARD_SIZE

        self.WINDOW_SIZE = self.CELL_SIZE * 20

        self.board_pixel = (self.BOARD_SIZE - 1) * self.CELL_SIZE

        self.MARGIN = (self.WINDOW_SIZE - self.board_pixel) // 2
        # ใน __init__
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
        def ease_out(t):
            return 1 - (1 - t) * (1 - t)

        # draw static stones ก่อน
        for x in range(self.game.BOARD_SIZE):
            for y in range(self.game.BOARD_SIZE):
                bit = 1 << (x * self.game.BOARD_SIZE + y)

                if self.game.black & bit or self.game.white & bit:
                    px = self.MARGIN + y * self.CELL_SIZE
                    py = self.MARGIN + x * self.CELL_SIZE

                    is_black = bool(self.game.black & bit)

                    # เช็คว่ามี animation อยู่ไหม
                    anim = next((a for a in self.animations if a["x"] == x and a["y"] == y), None)

                    if anim:
                        t = anim["time"] / 0.2  # duration 0.2s
                        t = min(t, 1.0)
                        t = ease_out(t)

                        # scale animation
                        scale = 0.5 + 0.5 * t

                        # reflection intensity
                        reflection = t

                        self.draw_animated_stone(px, py, radius, is_black, scale, reflection)
                    else:
                        self.draw_animated_stone(px, py, radius, is_black, 1.0, 1.0)

    def draw_animated_stone(self, px, py, radius, is_black, scale, reflection):
        r = int(radius * scale)

        # shadow
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

