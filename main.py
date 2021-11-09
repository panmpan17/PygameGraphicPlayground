from typing import List, Tuple
import pygame
import sys


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


class ClickablePoint(Point):
    def __init__(self, position, color=None, radius=3, width=2, hover_color=None, click_color=None, range=10):
        super().__init__(position=position, color=color, radius=radius, width=width)

        if hover_color is None:
            self.hover_color = Color.ORANGE
        else:
            self.hover_color = hover_color

        if click_color is None:
            self.click_color = Color.RED
        else:
            self.click_color = click_color

        self.status = 0
        self.range = 10

    def update(self, delta_time: float):
        sqrt_magnitude = (InputSystem.MOUSE_POS[0] - self.position[0]) ** 2 + (InputSystem.MOUSE_POS[1] - self.position[1]) ** 2

        if sqrt_magnitude <= (self.range * self.range):
            if self.status != 2:
                self.status = 1

                if InputSystem.MOUSE_DOWN:
                    self.status = 2
            else:
                if InputSystem.MOUSE_UP:
                    self.status = 0
        else:
            if self.status == 1:
                self.status = 0
            elif self.status == 2 and InputSystem.MOUSE_UP:
                self.status = 0

    def draw(self, window: "ManagedWindow"):
        if self.status == 0:
            pygame.draw.circle(window.surface, self.color, self.position, self.radius, self.width)
        elif self.status == 1:
            pygame.draw.circle(window.surface, self.hover_color, self.position, self.radius, self.width)
        elif self.status == 2:
            pygame.draw.circle(window.surface, self.click_color, self.position, self.radius, self.width)


class Anchor(Entity):
    def __init__(self, piviot_position, handle_poisition=None):
        self.piviot_point: ClickablePoint = ClickablePoint(piviot_position, radius=8, width=0, range=30)
        self.handle_point: ClickablePoint = ClickablePoint(handle_poisition, radius=6, range=30, color=Color.GRAY)
        self.line_color = Color.GRAY
        self.has_change = False
    
    def update(self,  delta_time: float):
        self.has_change = False
        self.piviot_point.update(delta_time)

        if self.piviot_point.status == 2:
            delta = (self.handle_point.position[0] - self.piviot_point.position[0],
                     self.handle_point.position[1] - self.piviot_point.position[1])
            self.piviot_point.position = InputSystem.MOUSE_POS
            self.handle_point.position = (InputSystem.MOUSE_POS[0] + delta[0], InputSystem.MOUSE_POS[1] + delta[1])
            self.has_change = True
        
        self.handle_point.update(delta_time)

        if self.handle_point.status == 2:
            self.handle_point.position = InputSystem.MOUSE_POS
            self.has_change = True

    def draw(self, window: "ManagedWindow"):
        pygame.draw.line(window.surface, self.line_color, self.piviot_point.position, self.handle_point.position)
        self.piviot_point.draw(window)
        self.handle_point.draw(window)


class BezeirCurveDebug(Entity):
    def __init__(self, anchor_1, anchor_2):
        self.anchor_1: Anchor = anchor_1
        self.anchor_2: Anchor = anchor_2

        self.percentage = 0.5
        self.percentage_forward = True
        self.percentage_speed = 0.3

        self.line_color = Color.GRAY
    
    def update(self,  delta_time: float):
        if self.percentage_forward:
            self.percentage += self.percentage_speed * delta_time
            if self.percentage >= 1:
                self.percentage = 1
                self.percentage_forward = False
        else:
            self.percentage -= self.percentage_speed * delta_time
            if self.percentage <= 0:
                self.percentage = 0
                self.percentage_forward = True

    def draw(self, window: "ManagedWindow"):
        pygame.draw.line(window.surface, self.line_color, self.anchor_1.handle_point.position, self.anchor_2.handle_point.position)

        center_1_1 = Math.lerp_point(self.anchor_1.piviot_point.position, self.anchor_1.handle_point.position, self.percentage)
        center_1_2 = Math.lerp_point(self.anchor_1.handle_point.position, self.anchor_2.handle_point.position, self.percentage)
        center_1_3 = Math.lerp_point(self.anchor_2.handle_point.position, self.anchor_2.piviot_point.position, self.percentage)

        pygame.draw.circle(window.surface, self.line_color, center_1_1, 3)
        pygame.draw.circle(window.surface, self.line_color, center_1_2, 3)
        pygame.draw.circle(window.surface, self.line_color, center_1_3, 3)

        pygame.draw.line(window.surface, self.line_color, center_1_1, center_1_2)
        pygame.draw.line(window.surface, self.line_color, center_1_2, center_1_3)

        center_2_1 = Math.lerp_point(center_1_1, center_1_2, self.percentage)
        center_2_2 = Math.lerp_point(center_1_2, center_1_3, self.percentage)

        pygame.draw.circle(window.surface, self.line_color, center_2_1, 3)
        pygame.draw.circle(window.surface, self.line_color, center_2_2, 3)

        pygame.draw.line(window.surface, self.line_color, center_2_1, center_2_2)

        center_3_1 = Math.lerp_point(center_2_1, center_2_2, self.percentage)
        pygame.draw.circle(window.surface, Color.YELLOW, center_3_1, 10)


class BezeirCurve(Entity):
    def __init__(self, anchor_1, anchor_2):
        self.anchor_1: Anchor = anchor_1
        self.anchor_2: Anchor = anchor_2

        self.lines = []
        self.iteration = 20

        self.recalculate_curve()

    def sample(self, percentage) -> Tuple[float, float]:
        center_1_1 = Math.lerp_point(self.anchor_1.piviot_point.position, self.anchor_1.handle_point.position, percentage)
        center_1_2 = Math.lerp_point(self.anchor_1.handle_point.position, self.anchor_2.handle_point.position, percentage)
        center_1_3 = Math.lerp_point(self.anchor_2.handle_point.position, self.anchor_2.piviot_point.position, percentage)

        center_2_1 = Math.lerp_point(center_1_1, center_1_2, percentage)
        center_2_2 = Math.lerp_point(center_1_2, center_1_3, percentage)

        return Math.lerp_point(center_2_1, center_2_2, percentage)
    
    def recalculate_curve(self):
        part = 1 / self.iteration

        self.lines.clear()
        
        # point_start = self.sample(0)
        # point_end = (0, 0)
        self.lines.append(self.sample(0))
        for i in range(1, self.iteration):
            point_end = self.sample(i * part)

            # self.lines.append((point_start, point_end))
            self.lines.append(self.sample(i * part))

            point_start = point_end
        
        self.lines.append(self.sample(1))
        # self.lines.append((point_start, self.sample(1)))
    
    def update(self, delta_time: float):
        self.anchor_1.update(delta_time)
        self.anchor_2.update(delta_time)

        if self.anchor_1.has_change or self.anchor_2.has_change:
            self.recalculate_curve()
    
    def draw(self, window: "ManagedWindow"):
        self.anchor_1.draw(window)
        self.anchor_2.draw(window)

        # for line in self.lines:
        #     pygame.draw.line(window.surface, Color.WHITE, line[0], line[1])
        pygame.draw.lines(window.surface, Color.WHITE, False, self.lines)


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


if __name__ == "__main__":
    window = ManagedWindow((700, 700))
    bezeir = BezeirCurve(Anchor((150, 150), (150, 200)), Anchor((250, 150), (250, 200)))
    # window.children.append(anchor_1)
    # window.children.append(anchor_2)
    window.children.append(BezeirCurveDebug(bezeir.anchor_1, bezeir.anchor_2))
    window.children.append(bezeir)
    window.run()
