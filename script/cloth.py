import pygame

from typing import List, Tuple

try:
    from .foundation import ManagedWindow, Entity, Color, Math, Vector
except ImportError:
    from foundation import ManagedWindow, Entity, Color, Math, Vector

class ClothNode:
    def __init__(self, position, velocity=(0, 0), acceration=(0, 0), magnitude=0, fixed=False) -> None:
        self.position = position
        self.velocity = velocity
        self.acceration = acceration
        self.magnitude = magnitude
        self.mass = 1

        self.fixed = fixed


class NodeConnection:
    def __init__(self, first_node:ClothNode, second_node:ClothNode):
        self.first_node: ClothNode = first_node
        self.second_node: ClothNode = second_node

        self.length = Math.magnitude(self.first_node.position, self.second_node.position)
        self.flexable_min = 0.9
        self.flexable_max = 1.1
    
    def clamp_second_node_position(self):
        if self.first_node.fixed and self.second_node.fixed:
            return

        elif self.first_node.fixed and not self.second_node.fixed:
            position_delta = Math.tuple_minus(self.second_node.position, self.first_node.position)
            self.second_node.position = Math.tuple_plus(self.first_node.position, Math.clamp_magnitude(
                position_delta, self.length * self.flexable_max,
                clamp_when_distance_over=True))

            new_delta = Math.clamp_magnitude(position_delta, self.length)
            new_position = Math.tuple_plus(self.first_node.position, new_delta)

            self.second_node.acceration = Math.tuple_plus(self.second_node.acceration, Math.tuple_minus(new_position, self.second_node.position))

        elif not self.first_node.fixed and self.second_node.fixed:
            position_delta = Math.tuple_minus(self.first_node.position, self.second_node.position)
            self.first_node.position = Math.tuple_plus(self.second_node.position, Math.clamp_magnitude(
                position_delta, self.length * self.flexable_max,
                clamp_when_distance_over=True))

            new_delta = Math.clamp_magnitude(position_delta, self.length)
            new_position = Math.tuple_plus(self.second_node.position, new_delta)

            self.first_node.acceration = Math.tuple_plus(self.first_node.acceration, Math.tuple_minus(new_position, self.first_node.position))
        
        else:
            position_delta = Math.tuple_minus(self.second_node.position, self.first_node.position)

            magnitude = Math.magnitude(position_delta)
            if magnitude > self.length * self.flexable_max:
                self.first_node.position, self.second_node.position = self.pull_two_point_together(
                    self.first_node.position, self.second_node.position, self.length * self.flexable_max)

            new_delta = Math.clamp_magnitude(position_delta, self.length)
            new_position = Math.tuple_plus(self.first_node.position, new_delta)
            self.second_node.acceration = Math.tuple_plus(self.second_node.acceration, Math.tuple_minus(new_position, self.second_node.position))

            new_delta = Math.clamp_magnitude(Math.tuple_multiple(position_delta, -1), self.length)
            new_position = Math.tuple_plus(self.second_node.position, new_delta)
            self.first_node.acceration = Math.tuple_plus(self.first_node.acceration, Math.tuple_minus(new_position, self.first_node.position))

    @staticmethod
    def pull_two_point_together(point_a, point_b, length_constain) -> Tuple[Vector, Vector]:
        center_position = Math.lerp_point(point_a, point_b, 0.5)

        point_a = Math.tuple_plus(center_position, Math.clamp_magnitude(
            Math.tuple_minus(point_a, center_position), length_constain / 2,
            clamp_when_distance_over=True))

        point_b = Math.tuple_plus(center_position, Math.clamp_magnitude(
            Math.tuple_minus(point_b, center_position), length_constain / 2,
            clamp_when_distance_over=True))
        
        return point_a, point_b


class Cloth(Entity):
    def __init__(self) -> None:
        self.points: List[ClothNode] = []
        self.connections: List[NodeConnection] = []

        self.set_2()

        self.gravity = (0, 10)
    
    def set_1(self):
        self.points.append(ClothNode((150, 40), fixed=True))
        self.points.append(ClothNode((130, 60), fixed=True))
        self.points.append(ClothNode((170, 60)))
        self.points.append(ClothNode((150, 80)))

        self.connect_point(self.points[0], self.points[1])
        self.connect_point(self.points[0], self.points[2])
        self.connect_point(self.points[1], self.points[3])
        self.connect_point(self.points[2], self.points[3])
    
    def set_2(self):
        x_size = 5
        y_size = 5

        point_matrix = [[None for i in range(x_size)] for e in range(y_size)]

        base_x = 100
        base_y = 40
        x_increment = 20
        y_increment = 20

        for x in range(x_size):
            for y in range(y_size):
                window_x = x * x_increment + base_x
                window_y = y * y_increment + base_y
                point_matrix[y][x] = ClothNode((window_x, window_y))
                self.points.append(point_matrix[y][x])

        point_matrix[0][0].fixed = True
        point_matrix[0][-1].fixed = True
        # point_matrix[-1][0].fixed = True
        # point_matrix[-1][-1].fixed = True

        for y in range(y_size - 1):
            for x in range(x_size - 1):
                self.connect_point(point_matrix[y][x], point_matrix[y][x + 1])
                self.connect_point(point_matrix[y][x], point_matrix[y + 1][x])

        for x in range(x_size - 1):
            self.connect_point(point_matrix[-1][x], point_matrix[-1][x + 1])
        for y in range(y_size - 1):
            self.connect_point(point_matrix[y][-1], point_matrix[y + 1][-1])
    
    def connect_point(self, first_node, second_node):
        self.connections.append(NodeConnection(
            first_node=first_node,
            second_node=second_node))

    def update(self, delta_time: float):
        for connection in self.connections:
            connection.clamp_second_node_position()

        for i, point in enumerate(self.points):
            if not point.fixed:
                point.acceration = Math.tuple_plus(point.acceration, self.gravity)
            
            point.velocity = Math.tuple_plus(point.velocity, Math.tuple_multiple(point.acceration, delta_time))
            point.position = Math.tuple_plus(point.position, Math.tuple_multiple(point.velocity, delta_time))
        #     pygame.draw.line(
        #         window.surface, Color.WHITE,
        #         connection.first_node.position, connection.second_node.position)

    def draw(self, window: ManagedWindow):
        for i, point in enumerate(self.points):
            if point.fixed:
                pygame.draw.circle(window.surface, Color.RED, point.position, radius=3)
            else:
                pygame.draw.circle(window.surface, Color.WHITE, point.position, radius=3)
            point.acceration = (0, 0)
        
        for connection in self.connections:
            pygame.draw.line(
                window.surface, Color.WHITE,
                connection.first_node.position, connection.second_node.position)


if __name__ == "__main__":
    window = ManagedWindow((300, 300), step_update=False, tick=30)

    window.children.append(Cloth())

    window.run()
