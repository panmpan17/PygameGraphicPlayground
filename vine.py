import pygame
import csv
import math

from typing import List, Tuple
from foundation import ManagedWindow, Entity, InputSystem, Color, Math
from bezier_curve import ClickablePoint


class Gizmos:
    Line = 1
    Dot = 2

    def __init__(self, type_, color, argument):
        self.type = type_
        self.color = color
        self.argument = argument


class VineNode:
    def __init__(self, position, velocity=(0, 0), acceration=(0, 0), magnitude=0) -> None:
        self.position = position
        self.velocity = velocity
        self.acceration = acceration
        self.magnitude = magnitude
        self.mass = 1


class Vine(Entity):
    def __init__(self, start_position, node_delta=(0, 25), length=10, gravity=(0, 10)):
        self.points: List[VineNode] = []

        self.points.append(VineNode(start_position))

        for _ in range(1, length):
            new_pos = (start_position[0] + node_delta[0], start_position[1] + node_delta[1])
            magnitude = Math.magnitude(start_position, new_pos)
            self.points.append(VineNode(new_pos, magnitude=magnitude))
            start_position = new_pos
        
        self.gizmos: List[Gizmos] = []
        self.gravity = gravity
        self.records = []

    def apply_force(self, force_center, force_radius, force_strength):
        for i, point in enumerate(self.points):
            sqr_magnitude = Math.sqr_magnitude(point.position, force_center)
            if sqr_magnitude <= force_radius * force_radius:
                point.velocity = Math.tuple_plus(point.velocity, force_strength)

                # for e in range(i + 1, len(self.points)):
                #     self.points[e].position = Math.tuple_plus(self.points[e].position, delta)
    
    def update(self, delta_time: float):
        pull_from = self.points[0].position
        pull_direction = (0, 1)

        self.gizmos.clear()

        for i, point in enumerate(self.points):
            if i == 0:
                continue

            pull_to = (pull_direction[0] * point.magnitude + pull_from[0], pull_direction[1] * point.magnitude + pull_from[1])
            # self.gizmos.append(Gizmos(Gizmos.Dot, Color.YELLOW, pull_to))

            acceleration = self.gravity
            # self.gizmos.append(Gizmos(Gizmos.Line, Color.RED, (point.position, Math.tuple_plus(point.position, self.gravity))))

            lift_delta = Math.tuple_multiple(Math.tuple_minus(pull_from, point.position), 0.3)
            acceleration = Math.tuple_plus(acceleration, lift_delta)
            # self.gizmos.append(Gizmos(Gizmos.Line, Color.GREEN, (point.position, Math.tuple_plus(point.position, lift_delta))))

            acceleration = Math.tuple_plus(acceleration, Math.tuple_minus(pull_to, point.position))
            # self.gizmos.append(Gizmos(Gizmos.Line, Color.BLUE, (point.position, pull_to)))

            point.velocity = Math.tuple_plus(point.velocity, Math.tuple_multiple(acceleration, delta_time))

            #  The new point should be, if without magnitude constrain
            suppose_point = Math.tuple_plus(point.position, Math.tuple_multiple(point.velocity, delta_time))

            # The new point constrain by  magnitude
            new_position = Math.tuple_plus(
                pull_from,
                Math.clamp_magnitude(
                    Math.tuple_minus(suppose_point, pull_from),
                    point.magnitude))

            # self.gizmos.append(Gizmos(Gizmos.Line, Color.YELLOW, (new_position, Math.tuple_plus(new_position, point.velocity))))

            # Calculate magnitude constrain translate in to velocity and acceleration
            length_fix_delta = Math.tuple_minus(new_position, suppose_point)

            # if length_fix_delta > 0.1:
            # Math.tuple_multiple(length_fix_delta, 10)
            # self.gizmos.append(Gizmos(Gizmos.Line, Color.PINK, (point.position, new_position)))

            point.velocity = Math.tuple_plus(point.velocity, Math.tuple_multiple(length_fix_delta, 1))
            # point.velocity = Math.tuple_plus(point.velocity, Math.tuple_multiple(Math.tuple_minus(new_position, point.position), 1))

            # self.gizmos.append(Gizmos(Gizmos.Line, Color.ORANGE, (point.position, Math.tuple_plus(point.position, acceleration))))
            # point.velocity = Math.tuple_plus(point.velocity, length_fix_delta)

            delta = Math.tuple_minus(new_position, point.position)
            point.position = new_position

            for e in range(i + 1, len(self.points)):
                self.points[e].position = Math.tuple_plus(self.points[e].position, delta)
            # self.records.append((*point.position, *point.velocity, Math.magnitude(point.velocity)))

            pull_direction = Math.normalize(Math.tuple_minus(point.position, pull_from))
            pull_from = point.position

    def draw(self, window: ManagedWindow):
        for i, point in enumerate(self.points):
            # pygame.draw.circle(window.surface, Color.WHITE, point.position, radius=3)

            if i != 0:
                pygame.draw.line(window.surface, Color.WHITE, self.points[i - 1].position, point.position)
        
        for gizmos in self.gizmos:
            if gizmos.type == Gizmos.Line:
                pygame.draw.line(window.surface, gizmos.color, gizmos.argument[0], gizmos.argument[1])
            elif gizmos.type == Gizmos.Dot:
                pygame.draw.circle(window.surface, gizmos.color, gizmos.argument, radius=3)

    def save_records(self):
        with open("result.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(("X", "Y", "X Velocity", "Y Velocity", "Velocity magnitude"))
            writer.writerows(self.records)
        # print(self.records)


class FakeCollider(ClickablePoint):
    def __init__(self, position, **kwargs):
        super().__init__(position, **kwargs)

        self.vines: List[Vine] = []

    def update(self, delta_time: float):
        super().update(delta_time)

        if self.status == 2:
            delta = Math.tuple_minus(InputSystem.MOUSE_POS, self.position)
            self.position = InputSystem.MOUSE_POS

            for vine in self.vines:
                vine.apply_force(self.position, self.radius, delta)

    def draw(self, window: "ManagedWindow"):
        super().draw(window)


if __name__ == "__main__":
    window = ManagedWindow((300, 300), step_update=True, tick=30)
    # vine = Vine((150, 10), node_delta=(6, 8), length=20, gravity=(0, 30))
    # vine.update(0)
    # window.children.append(Vine((150, 10), node_delta=(6, 8), length=20, gravity=(0, 30)))

    collider = FakeCollider((50, 100), color=Color.GREEN, radius=15, width=2, click_color=Color.RED, range=15)

    for x in range(100, 210, 10):
        vine = Vine((x, 10), node_delta=(6, 8), length=20, gravity=(0, 30))
        window.children.append(vine)
        collider.vines.append(vine)

    window.children.append(collider)

    window.run()

    vine.save_records()
