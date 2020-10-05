import random
from math import sqrt


def distance(p1, p2):
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def point(margin):
    return [random.randint(10 + margin, 100 - margin - 15) / 2, random.randint(10, 70)]


def add_point(points, d, margin):
    M = 100
    done = False
    c = 0
    while not done and c < M:
        c += 1
        p = point(margin)
        for pc in points:
            if distance(pc, p) < d:
                done = False
                break
            else:
                done = True
    if c < M:
        p[0] = p[0]
        points.append(p)
    # return points


def get_points(N, d=10, margin=10):
    points = []
    c = 0
    while len(points) != N and c < 50:
        c += 1
        points = []
        points.append(point(margin))
        [add_point(points, d, margin) for i in range(int(N) - 1)][-1]

        if len(points) == N:
            break

    return points
