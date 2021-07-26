import random
from math import sqrt
from typing import TypeVar, Union, List

POINT = TypeVar("(p1, p2) point")


# ----------------------------------------------------------------------
def distance(p1: POINT, p2: POINT) -> float:
    """Euclidean distance."""
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


# ----------------------------------------------------------------------
def point(margin: Union[float, int]) -> POINT:
    """Generate a random point, inside a fixed area."""
    return [random.uniform(0 + margin / 2, 7.2 - margin / 2), random.uniform(0 + margin / 2, 13.5 - margin / 2)]


# ----------------------------------------------------------------------
def add_point(points: List[POINT], d: Union[float, int], margin: Union[float, int]) -> None:
    """Add a point that comply with the rule of minimum distance."""
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


# ----------------------------------------------------------------------
def get_points(N: int, d: Union[float, int], margin: Union[float, int]) -> List[POINT]:
    """Generate N points that comply with the rule of minimum distance."""
    points = []
    c = 0
    while len(points) != N and c < 50:
        c += 1
        points = []
        points.append(point(margin))
        if N > 1:
            [add_point(points, d, margin) for i in range(int(N) - 1)][-1]

        if len(points) == N:
            break

    return points
