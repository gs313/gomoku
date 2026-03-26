import pygame

class GameUI:
    def __init__(self, game):
        self.game = game

        self.CELL_SIZE = 30
        self.MARGIN = 40
        self.SIZE = game.BOARD_SIZE * self.CELL_SIZE + self.MARGIN * 2

        pygame.init()
        self.screen = pygame.display.set_mode((self.SIZE, self.SIZE))

    def draw_board(self):
        self.screen.fill((200,170,120))

        for i in range(self.game.BOARD_SIZE):
            pygame.draw.line(self.screen, (0,0,0),
                (self.MARGIN, self.MARGIN + i*self.CELL_SIZE),
                (self.SIZE - self.MARGIN, self.MARGIN + i*self.CELL_SIZE))

            pygame.draw.line(self.screen, (0,0,0),
                (self.MARGIN + i*self.CELL_SIZE, self.MARGIN),
                (self.MARGIN + i*self.CELL_SIZE, self.SIZE - self.MARGIN))

    def draw_stones(self):
        for x in range(self.game.BOARD_SIZE):
            for y in range(self.game.BOARD_SIZE):
                bit = 1 << (x * self.game.BOARD_SIZE + y)

                px = self.MARGIN + y * self.CELL_SIZE
                py = self.MARGIN + x * self.CELL_SIZE

                if self.game.black & bit:
                    pygame.draw.circle(self.screen, (0,0,0), (px, py), 12)

                elif self.game.white & bit:
                    pygame.draw.circle(self.screen, (255,255,255), (px, py), 12)

    def get_cell(self, pos):
        mx, my = pos
        x = round((my - self.MARGIN) / self.CELL_SIZE)
        y = round((mx - self.MARGIN) / self.CELL_SIZE)

        if 0 <= x < self.game.BOARD_SIZE and 0 <= y < self.game.BOARD_SIZE:
            return x, y
        return None