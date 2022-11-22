import math
from typing import List
import pygame

from foundation import ManagedWindow, Entity, Color, Vector3D, InputSystem


class Cube:
    def __init__(self, position: Vector3D, size):
        self.position: Vector3D = position
        self.size = size

        x, y, z = position

        self.positions: List[Vector3D] = [
            (x + size, y + size, z + size), # 0
            (x - size, y + size, z + size), # 1
            (x + size, y - size, z + size), # 2
            (x - size, y - size, z + size), # 3
            (x + size, y + size, z - size), # 4
            (x - size, y + size, z - size), # 5
            (x + size, y - size, z - size), # 6
            (x - size, y - size, z - size), # 7
        ]

        self.lines = [
            (0, 1),
            (0, 2),
            (0, 4),

            (1, 3),
            (1, 5),

            (2, 3),
            (2, 6),

            (3, 7),

            (4, 5),
            (4, 6),

            (5, 7),

            (6, 7),
        ]


class Camera(Entity):
    def __init__(self, position: Vector3D):
        self.position: Vector3D = position
        self.move_speed: Vector3D = (10, 10, 1)

        self.render_objects: List[Cube] = []
        self.scale = 10

    def update(self, delta_time: float):
        delta_x = 0
        delta_y = 0
        delta_z = 0
        if InputSystem.KEY_A:
            delta_x += self.move_speed[0]
        if InputSystem.KEY_D:
            delta_x -= self.move_speed[0]

        if InputSystem.KEY_Q:
            delta_y -= self.move_speed[1]
        if InputSystem.KEY_E:
            delta_y += self.move_speed[1]

        if InputSystem.KEY_W:
            delta_z -= self.move_speed[2]
        if InputSystem.KEY_S:
            delta_z += self.move_speed[2]
        
        self.position = self.position[0] + (delta_x * delta_time), self.position[1] + (delta_y * delta_time), self.position[2] + (delta_z * delta_time)

    def draw(self, window: ManagedWindow):
        for render_object in self.render_objects:
            self.draw_object(window, render_object)
    
    def draw_object(self, window: ManagedWindow, render_object: Cube):
        center = window.size[0] / 2, window.size[1] / 2

        transformed_points = []
        for point in render_object.positions:
            delta = (point[0] - self.position[0], point[1] - self.position[1], point[2] - self.position[2])
            multiplier = math.fabs(delta[2] / self.position[2])

            transformed_point = (
                center[0] - (delta[0] / multiplier * self.scale),
                center[1] - (delta[1] / multiplier * self.scale))

            transformed_points.append(transformed_point)
        
        for line in render_object.lines:
            pygame.draw.line(window.surface, Color.WHITE, transformed_points[line[0]], transformed_points[line[1]])


class App:
    def main(self):
        window = ManagedWindow((400, 400), step_update=False, tick=30)

        cube = Cube((0, 0, 40), 10)
        camera = Camera((0, 0, -10))
        camera.render_objects.append(cube)
        window.children.append(camera)

        window.run()


if __name__ == "__main__":
    app = App()
    app.main()

