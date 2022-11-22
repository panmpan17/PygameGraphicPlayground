from os import stat
import pygame
import sys

from typing import List, Tuple


class Color:
    WHITE = (255, 255, 255)
    ORANGE = (255, 200, 0)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    PINK = (255, 230, 230)


Vector = Tuple[int, int]
Vector3D = Tuple[float, float, float]


class Math:
    @staticmethod
    def lerp(a: float, b: float, percentage: float) -> float:
        return (b - a) * percentage + a

    @staticmethod
    def lerp_point(point_a: Vector, point_b: Vector, percentage: float) -> Vector:
        return (Math.lerp(point_a[0], point_b[0], percentage), Math.lerp(point_a[1], point_b[1], percentage))

    @staticmethod
    def magnitude(point_a: Vector, point_b: Vector=None) -> float:
        if point_b is None:
            return (point_a[0] ** 2 + point_a[1] ** 2) ** 0.5
        else:
            return ((point_a[0] - point_b[0]) ** 2 + (point_a[1] - point_b[1]) ** 2) ** 0.5

    @staticmethod
    def sqr_magnitude(point_a: Vector, point_b: Vector) -> float:
        return (point_a[0] - point_b[0]) ** 2 + (point_a[1] - point_b[1]) ** 2
    
    @staticmethod
    def clamp_magnitude(vector: Vector, clamp_distance: float, clamp_when_distance_over: bool=False) -> Vector:
        distance = (vector[0] ** 2 + vector[1] ** 2) ** 0.5

        if clamp_when_distance_over and distance < clamp_distance:
            return vector

        magnitude_multiplier = distance / clamp_distance
        return (vector[0] / magnitude_multiplier, vector[1] / magnitude_multiplier)

    @staticmethod
    def tuple_multiple(point_a: Vector, point_b: Vector | float) -> Vector:
        if isinstance(point_b, float) or isinstance(point_b, int):
            return (point_a[0] * point_b, point_a[1] * point_b)
        else:
            return (point_a[0] * point_b[0], point_a[1] * point_b[1])

    @staticmethod
    def tuple_plus(point_a: Vector, point_b: Vector) -> Vector:
        return (point_a[0] + point_b[0], point_a[1] + point_b[1])

    @staticmethod
    def tuple_minus(point_a: Vector, point_b: Vector) -> Vector:
        return (point_a[0] - point_b[0], point_a[1] - point_b[1])

    @staticmethod
    def normalize(vector: Vector) -> Vector:
        magnitude = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
        return (vector[0] / magnitude, vector[1] / magnitude)


class InputSystem:
    MOUSE_DOWN = False
    MOUSE_UP = False
    MOUSE_POS = (0, 0)

    KEY_A = False
    KEY_D = False
    KEY_E = False
    KEY_Q = False
    KEY_S = False
    KEY_W = False


class Entity:
    def update(self,  delta_time: float):
        raise NotImplementedError("Draw function not implemented")

    def draw(self, window: "ManagedWindow"):
        raise NotImplementedError("Draw function not implemented")


class Point(Entity):
    def __init__(self, position, color=None, radius=3, width=2):
        self.position = position

        if color is None:
            self.color = Color.WHITE
        else:
            self.color = color
        
        self.radius = radius
        self.width = width

    def update(self, delta_time: float):
        pass

    def draw(self, window: "ManagedWindow"):
        pygame.draw.circle(window.surface, self.color, self.position, self.radius, self.width)

class ManagedWindow:
    def __init__(self, size: Vector, step_update=False, tick=30) -> None:
        self.size = size
        self.full_rect = (0, 0, *size)
        self.surface: pygame.Surface = None
        self.background_color = Color.BLACK

        self.children: List[Entity] = []

        self.step_update = step_update

        self.tick = tick

        pygame.init()

    def run(self):
        self.surface = pygame.display.set_mode(self.size)

        clock = pygame.time.Clock()

        while True:
            InputSystem.MOUSE_DOWN = False
            InputSystem.MOUSE_UP = False
            update_key_pressed = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    InputSystem.MOUSE_DOWN = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    InputSystem.MOUSE_UP = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        InputSystem.KEY_A = True
                    elif event.key == pygame.K_d:
                        InputSystem.KEY_D = True
                    elif event.key == pygame.K_e:
                        InputSystem.KEY_E = True
                    elif event.key == pygame.K_q:
                        InputSystem.KEY_Q = True
                    elif event.key == pygame.K_s:
                        InputSystem.KEY_S = True
                    elif event.key == pygame.K_w:
                        InputSystem.KEY_W = True

                    elif event.key == pygame.K_SPACE:
                        update_key_pressed = True
                    elif event.key == pygame.K_RETURN:
                        self.step_update = not self.step_update

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        InputSystem.KEY_A = False
                    elif event.key == pygame.K_d:
                        InputSystem.KEY_D = False
                    elif event.key == pygame.K_e:
                        InputSystem.KEY_E = False
                    elif event.key == pygame.K_q:
                        InputSystem.KEY_Q = False
                    elif event.key == pygame.K_s:
                        InputSystem.KEY_S = False
                    elif event.key == pygame.K_w:
                        InputSystem.KEY_W = False

            InputSystem.MOUSE_POS = pygame.mouse.get_pos()
            
            pygame.draw.rect(self.surface, self.background_color, self.full_rect)

            for child in self.children:
                if self.step_update:
                    if update_key_pressed:
                        child.update(1 / 30)
                else:
                    child.update(1 / 30)

                child.draw(self)

            pygame.display.flip()
            clock.tick(self.tick)

