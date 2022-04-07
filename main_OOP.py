import pygame
import random


class Display:
    width = 640
    height = 480
    fps = 30
    caption = "Snaek"

    def __init__(self, width: int = None, height: int = None, fps: int = None, caption: str = None):
        self.width = self.width if width is None else width
        self.height = self.height if height is None else height
        self.fps = self.fps if fps is None else fps
        self.caption = self.caption if caption is None else caption


class Position:
    def __init__(self, x: int = None, y: int = None):
        self.x = x
        self.y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value: int):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value: int):
        self._y = value

    def set(self, value: tuple or list):
        self.x, self.y = value

    def get(self):
        return self.x, self.y

    def random(self, min_max_x: tuple, min_max_y: tuple):
        self.set((
            round(random.randrange(min_max_x[0], min_max_x[1]) / 10) * 10,
            round(random.randrange(min_max_y[0], min_max_y[1]) / 10) * 10
        ))


class Food:
    eaten = 0

    def __init__(self, size=None):
        self.size = (10, 10) if size is None else size
        self.pos = Position()
        self.generate_pos()

    def generate_pos(self):
        self.pos.random(
            (0, Display.width - self.size[0]),
            (0, Display.height - self.size[1])
        )


class Snake:
    def __init__(self, size: tuple or list = None, speed: int or float = None, position: tuple = None,
                 x_change=None, y_change=None):
        self.size = (10, 10) if size is None else size
        self.moving = False
        self.speed = 10 if speed is None else speed
        self.x_change = 0 if x_change is None else x_change
        self.y_change = 0 if y_change is None else y_change
        self.tails = list()
        if position is None:
            position = None, None

        self.pos = Position(position[0], position[1])

    # direction: up | down | left | right
    def direction(self, direction: str):
        self.moving = True
        if direction == "left" and self.x_change == 0:
            self.x_change = -self.speed
            self.y_change = 0
        elif direction == "right" and self.x_change == 0:
            self.x_change = self.speed
            self.y_change = 0
        elif direction == "up" and self.y_change == 0:
            self.x_change = 0
            self.y_change = -self.speed
        elif direction == "down" and self.y_change == 0:
            self.x_change = 0
            self.y_change = self.speed
        else:
            return False

    # updating position - moving if direction is chosen
    # TODO: обчислення позиції з урахуванням швидкості та перевірки чи виходить змійка за межі
    def update_position(self):
        if self.moving:
            # move snake tails
            ltx = self.pos.x
            lty = self.pos.y

            for i, v in enumerate(self.tails):
                _ltx = self.tails[i][0]
                _lty = self.tails[i][1]

                self.tails[i] = ltx, lty

                ltx = _ltx
                lty = _lty

            self.pos.x += self.x_change
            self.pos.y += self.y_change

            # teleport snake, if required
            if self.pos.x < 0:
                self.pos.x = Display.width
            elif self.pos.x > Display.width - self.size[0]:
                self.pos.x = 0
            elif self.pos.y < 0:
                self.pos.y = Display.height
            elif self.pos.y > Display.height - self.size[1]:
                self.pos.y = 0

            self.detect_tail_collision()

    def detect_tail_collision(self):
        # detect collision with tail
        for i, v in enumerate(self.tails):
            if self.pos.x + self.x_change == self.tails[i][0] and \
                    self.pos.y + self.y_change == self.tails[i][1]:
                self.tails = self.tails[:i]
                break

    def length(self):
        return len(self.tails)

    def generate_pos(self):
        self.pos.random(
            (0, Display.width - self.size[0]),
            (0, Display.height - self.size[1])
        )

    def add_tail_section(self):
        x = self.pos.x + self.size[0] + 10 * self.length()
        y = self.pos.y
        if x > Display.width:
            x -= Display.width
        self.tails.append([x, y])


class Game:
    colors = {
        "snake_head": (0, 255, 0),
        "snake_tail": (0, 200, 0),
        "food":       (255, 0, 0)
    }

    def __init__(self, width: int = None, height: int = None, fps: int = None):
        pygame.init()
        self.clock = pygame.time.Clock()

        self.title = "Snaek"
        self.ended = False
        self.paused = False

        self.display = Display(width, height, fps, self.title)
        self.display.init = pygame.display.set_mode((self.display.width, self.display.height))
        self.update_caption()
        pygame.display.update()

        self.snake = Snake()
        self.snake.generate_pos()

        self.food = Food()
        self.food.generate_pos()

        # self.snakes = list()
        #
        # self.foods = list()
        # for i in range(4):
        #     snake = Snake()
        #     snake.generate_pos()
        #     self.snakes.append(snake)
        #
        #     food = Food()
        #     food.generate_pos()
        #     self.foods.append(food)

        self.welcome()

        self.mainloop()

    # setting default values
    def set_defaults(self):
        pass

    def mainloop(self):
        while not self.ended:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.pause()
                    elif not self.paused:
                        if event.key == pygame.K_LEFT:
                            self.snake.direction('left')
                        elif event.key == pygame.K_RIGHT:
                            self.snake.direction('right')
                        elif event.key == pygame.K_UP:
                            self.snake.direction('up')
                        elif event.key == pygame.K_DOWN:
                            self.snake.direction('down')
            if self.paused:
                continue

            self.display.init.fill((0, 0, 0))

            self.snake.update_position()

            # draw snake and tails
            self.draw_snake(self.snake)

            # draw food
            self.draw_food(self.food)

            # detect collision with food
            if self.snake.pos.x == self.food.pos.x and self.snake.pos.y == self.food.pos.y:
                self.eat_food(self.snake, self.food)

            self.update_caption({
                'Food': Food.eaten,
                'Length': 0 if self.snake.length() == 0 else self.snake.length()
            })
            pygame.display.update()
            self.clock.tick(self.display.fps)

    def update_caption(self, args: dict = None):
        result = f'{self.title}'
        if args is not None:
            for key, value in args.items():
                if key == '':
                    result += f' | {value}'
                else:
                    result += f' | {key}: {value}'
        pygame.display.set_caption(result)

    def pause(self):
        self.paused = not self.paused
        self.update_caption({'': 'Paused'})

    def welcome(self):
        print(f'Welcome to {self.title}!')
        a = True if input("Do you wanna some cheats? (y/n)\n > ").lower() == 'y' else False
        if a:
            for i in range(70):
                self.snake.add_tail_section()


    def exit(self):
        self.ended = True
        print('See you next time!')

    def show_menu(self):
        pass

    @staticmethod
    def eat_food(snake: Snake, food: Food):
        Food.eaten += 1
        snake.tails.append([food.pos.x, food.pos.y])

        food.generate_pos()

    def draw_rect(self, color: tuple, pos: list):
        pygame.draw.rect(self.display.init, color, pos)

    def draw_snake(self, snake: Snake):
        # draw snake
        self.draw_rect(self.colors["snake_head"], [snake.pos.x, snake.pos.y, snake.size[0], snake.size[1]])

        # draw snake tails
        for t in self.snake.tails:
            self.draw_rect(self.colors["snake_tail"], [t[0], t[1], snake.size[0], snake.size[1]])

    def draw_food(self, food: Food):
        self.draw_rect(self.colors["food"], [food.pos.x, food.pos.y, food.size[0], food.size[1]])


game = Game()
