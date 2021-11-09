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


class Math:
    @staticmethod
    def lerp(a: float, b: float, percentage: float) -> float:
        delta = b - a
        return a + percentage * delta

    @staticmethod
    def lerp_point(point_a: Tuple[int, int], point_b: Tuple[int, int], percentage: float) -> Tuple[int, int]:
        return (Math.lerp(point_a[0], point_b[0], percentage), Math.lerp(point_a[1], point_b[1], percentage))


class InputSystem:
    MOUSE_DOWN = False
    MOUSE_UP = False
    MOUSE_POS = (0, 0)


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
    def __init__(self, size: Tuple[int, int]) -> None:
        self.size = size
        self.full_rect = (0, 0, *size)
        self.surface: pygame.Surface = None
        self.background_color = Color.BLACK

        self.children: List[Entity] = []

        pygame.init()

    def run(self):
        self.surface = pygame.display.set_mode(self.size)

        clock = pygame.time.Clock()

        while True:
            InputSystem.MOUSE_DOWN = False
            InputSystem.MOUSE_UP = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    InputSystem.MOUSE_DOWN = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    InputSystem.MOUSE_UP = True

            InputSystem.MOUSE_POS = pygame.mouse.get_pos()
            
            pygame.draw.rect(self.surface, self.background_color, self.full_rect)

            for child in self.children:
                child.update(1 / 30)
                child.draw(self)

            pygame.display.flip()
            clock.tick(30)

