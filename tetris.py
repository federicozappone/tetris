import pygame
import random
import time


class Tetris:
    def __init__(self, width, height, grid_size):
        self.WIDTH = width
        self.HEIGHT = height
        self.GRID_SIZE = grid_size
        self.GRID_WIDTH = width // grid_size
        self.GRID_HEIGHT = height // grid_size
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.SHAPES = [
            [[1, 1, 1, 1]],  # I
            [[1, 1, 1], [1, 0, 0]],  # J
            [[1, 1, 1], [0, 0, 1]],  # L
            [[1, 1], [1, 1]],  # O
            [[0, 1, 1], [1, 1, 0]],  # S
            [[1, 1, 1], [0, 1, 0]],  # T
            [[1, 1, 0], [0, 1, 1]],  # Z
        ]
        self.COLORS = [
            (0, 255, 255),  # Cyan (I)
            (0, 0, 255),  # Blue (J)
            (255, 165, 0),  # Orange (L)
            (255, 255, 0),  # Yellow (O)
            (0, 255, 0),  # Green (S)
            (128, 0, 128),  # Purple (T)
            (255, 0, 0),  # Red (Z)
        ]
        self.POINTS = [40, 100, 300, 1200]

        self.SCORE = 0
        self.LEVEL = 0
        self.MAX_LOCK_DELAY = 180

    def draw_grid(self, screen):
        for x in range(0, self.WIDTH, self.GRID_SIZE):
            pygame.draw.line(screen, self.WHITE, (x, 0), (x, self.HEIGHT))
        for y in range(0, self.HEIGHT, self.GRID_SIZE):
            pygame.draw.line(screen, self.WHITE, (0, y), (self.WIDTH, y))

    def draw_tetromino(self, screen, tetromino, x, y, color, scale=1.0):
        for row in range(len(tetromino)):
            for col in range(len(tetromino[row])):
                if tetromino[row][col]:
                    pygame.draw.rect(
                        screen,
                        color,
                        (
                            x + col * (self.GRID_SIZE * scale),
                            y + row * (self.GRID_SIZE * scale),
                            (self.GRID_SIZE * scale),
                            (self.GRID_SIZE * scale),
                        ),
                    )

    def is_valid_position(self, matrix, tetromino, x, y):
        for row in range(len(tetromino)):
            for col in range(len(tetromino[row])):
                if tetromino[row][col]:
                    if (
                        x + col < 0
                        or x + col >= self.GRID_WIDTH
                        or y + row >= self.GRID_HEIGHT
                    ):
                        return False
                    if matrix[y + row][x + col]:
                        return False
        return True

    def clear_rows(self, matrix, matrix_colors, rows):
        for row in rows:
            del matrix[row]
            del matrix_colors[row]
            matrix.insert(0, [0] * self.GRID_WIDTH)
            matrix_colors.insert(0, [0, 0, 0] * self.GRID_WIDTH)

    def get_speed(self):
        return (725 * 0.85**self.LEVEL + self.LEVEL) / 1000.0

    def get_score(self, num_rows):
        score = self.POINTS[num_rows - 1] + (self.LEVEL * self.POINTS[num_rows - 1])
        return score

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        matrix = [[0] * self.GRID_WIDTH for _ in range(self.GRID_HEIGHT)]
        matrix_colors = [[0, 0, 0] * self.GRID_WIDTH for _ in range(self.GRID_HEIGHT)]

        picks = [random.randint(0, 6), random.randint(0, 6)]

        pick = picks.pop(0)
        picks.append(random.randint(0, 6))

        tetromino = self.SHAPES[pick]
        tetromino_color = self.COLORS[pick]
        x, y = self.GRID_WIDTH // 2 - len(tetromino[0]) // 2, 0

        game_over = False

        last_update = time.time()
        lock_delay = 0

        current_level_lines = 0

        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a and self.is_valid_position(
                        matrix, tetromino, x - 1, y
                    ):
                        x -= 1
                        lock_delay = 0  # Reset lock delay on movement
                    if event.key == pygame.K_d and self.is_valid_position(
                        matrix, tetromino, x + 1, y
                    ):
                        x += 1
                        lock_delay = 0  # Reset lock delay on movement
                    if event.key == pygame.K_w:
                        rotated = list(zip(*reversed(tetromino)))
                        if self.is_valid_position(matrix, rotated, x, y):
                            tetromino = rotated
                            lock_delay = 0  # Reset lock delay on rotation
                    if event.key == pygame.K_SPACE:
                        while self.is_valid_position(matrix, tetromino, x, y + 1):
                            y += 1
                            # Ignore the lock delay if space is pressed
                            lock_delay = self.MAX_LOCK_DELAY

            speed_mult = 1

            keys = pygame.key.get_pressed()
            if keys[pygame.K_s]:
                speed_mult = 15

            if self.is_valid_position(matrix, tetromino, x, y + 1):
                if time.time() - last_update >= self.get_speed() / speed_mult:
                    y += 1
                    last_update = time.time()
                    lock_delay = 0  # Reset lock delay on downward movement
            else:
                lock_delay += 1

                if lock_delay >= self.MAX_LOCK_DELAY:
                    for row in range(len(tetromino)):
                        for col in range(len(tetromino[row])):
                            if tetromino[row][col]:
                                matrix[y + row][x + col] = 1
                                matrix_colors[y + row][x + col] = tetromino_color

                    # Check for completed rows
                    completed_rows = [i for i, row in enumerate(matrix) if all(row)]
                    if completed_rows:
                        current_level_lines += len(completed_rows)
                        self.clear_rows(matrix, matrix_colors, completed_rows)
                        self.SCORE += self.get_score(len(completed_rows))

                    if current_level_lines >= self.LEVEL * 5:
                        self.LEVEL += 1
                        current_level_lines = 0

                    pick = picks.pop(0)
                    tetromino = self.SHAPES[pick]
                    tetromino_color = self.COLORS[pick]
                    picks.append(random.randint(0, 6))
                    x, y = self.GRID_WIDTH // 2 - len(tetromino[0]) // 2, 0
                    lock_delay = 0  # Reset lock delay when a new piece spawns

                    if not self.is_valid_position(matrix, tetromino, x, y):
                        game_over = True

            screen.fill(self.BLACK)
            self.draw_grid(screen)

            for row in range(self.GRID_HEIGHT):
                for col in range(self.GRID_WIDTH):
                    if matrix[row][col]:
                        pygame.draw.rect(
                            screen,
                            matrix_colors[row][col],
                            (
                                col * self.GRID_SIZE,
                                row * self.GRID_SIZE,
                                self.GRID_SIZE,
                                self.GRID_SIZE,
                            ),
                        )

            # Draw next piece
            self.draw_tetromino(
                screen,
                self.SHAPES[picks[0]],
                8 * self.GRID_SIZE,
                1 * self.GRID_SIZE,
                self.COLORS[picks[0]],
                scale=0.5,
            )
            self.draw_tetromino(
                screen,
                tetromino,
                x * self.GRID_SIZE,
                y * self.GRID_SIZE,
                tetromino_color,
            )

            pygame.display.set_caption(f"Level: {self.LEVEL}   Score: {self.SCORE}")
            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    game = Tetris(801, 1600, 80)
    game.run()
