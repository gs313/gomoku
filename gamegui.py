import pygame

class GameUI:
    def __init__(self, game):
        self.game = game
        self.CELL_SIZE = 100
        self.BOARD_SIZE = game.BOARD_SIZE

        self.WINDOW_SIZE = self.CELL_SIZE * 20

        self.board_pixel = (self.BOARD_SIZE - 1) * self.CELL_SIZE

        self.MARGIN = (self.WINDOW_SIZE - self.board_pixel) // 2

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
        for x in range(self.game.BOARD_SIZE):
            for y in range(self.game.BOARD_SIZE):
                bit = 1 << (x * self.game.BOARD_SIZE + y)

                px = self.MARGIN + y * self.CELL_SIZE
                py = self.MARGIN + x * self.CELL_SIZE

                if self.game.black & bit:
                    pygame.draw.circle(self.screen, (0,0,0), (px, py), self.CELL_SIZE // 3)

                elif self.game.white & bit:
                    pygame.draw.circle(self.screen, (255,255,255), (px, py), self.CELL_SIZE // 3)

    def get_cell(self, pos):
        mx, my = pos

        x = int((my - self.MARGIN + self.CELL_SIZE/2) // self.CELL_SIZE)
        y = int((mx - self.MARGIN + self.CELL_SIZE/2) // self.CELL_SIZE)

        if 0 <= x < self.game.BOARD_SIZE and 0 <= y < self.game.BOARD_SIZE:
            return x, y
        return None