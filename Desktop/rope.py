import pygame


class Rope:
    def __init__(self, rod_pos, segments=20, length=400):
        self.length = length
        self.segment_length = length / segments
        self.points = []
        self.old_points = []

        for i in range(segments + 1):
            p = pygame.Vector2(rod_pos.x, rod_pos.y + i * self.segment_length)
            self.points.append(p)
            self.old_points.append(p.copy())

    def update(self, rod_top, bait_pos, bait_speed):
        wiggle = 0.2 + min(0.8, bait_speed / 30.0)
        gravity = pygame.Vector2(0, 0.4)
        segment_len = self.length / (len(self.points) - 1)

        for i in range(1, len(self.points) - 1):
            joint = self.points[i]
            velocity = (joint - self.old_points[i]) * 0.98
            self.old_points[i] = joint.copy()
            joint += velocity * (1 - wiggle) + gravity

        last = len(self.points) - 1
        for _ in range(4):
            self.points[0] = rod_top
            self.points[-1] = bait_pos

            for i in range(last):
                delta = self.points[i + 1] - self.points[i]
                dist = delta.length()
                if dist == 0:
                    continue
                correction = delta * 0.5 * ((dist - segment_len) / dist) * wiggle
                if i != 0:
                    self.points[i] += correction
                if i + 1 != last:
                    self.points[i + 1] -= correction

    def draw(self, screen, depth):
        width = int(1 + (1 - depth) * 3)
        pygame.draw.lines(screen, (254, 254, 254), False, self.points, width)