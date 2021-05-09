import numbers
import struct
from abc import ABCMeta, abstractmethod
from functools import reduce
from math import cos, radians, sin, sqrt, floor


def render(*args):
    return fragment(*args).render()


def renderBinary(*args):
    return fragment(*args).renderBinary()


class EqualityMixin:
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__class__.__name__) + "{" + ", ".join(
            [f"{key}={value}" for key, value in self.__dict__.items()]) + "}"


class Renderable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def render(self): raise NotImplementedError

    @abstractmethod
    def renderBinary(self): raise NotImplementedError


class fragment(Renderable, EqualityMixin):
    def __init__(self, *children):
        self._children = children

    def render(self):
        return "\n".join(map(lambda child: child.render(), self._children))

    def renderBinary(self):
        return reduce(lambda result, next: result + next.renderBinary(), self._children, bytearray())


class vertex(Renderable, EqualityMixin):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def render(self):
        return f"vertex {float(self.x)} {float(self.y)} {float(self.z)}"

    def renderBinary(self):
        pack = struct.Struct('<f').pack
        return bytearray(pack(self.x)) + \
               bytearray(pack(self.y)) + \
               bytearray(pack(self.z))

    def __add__(self, other):
        if isinstance(other, vertex):
            return vertex(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            raise ValueError(f"unsupported operand type(s) for +: 'vertex' and '{type(other).__name__}'")

    def __sub__(self, other):
        if isinstance(other, vertex):
            return vertex(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            raise ValueError(f"unsupported operand type(s) for -: 'vertex' and '{type(other).__name__}'")

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return vertex(self.x * other, self.y * other, self.z * other)
        if isinstance(other, vertex):
            return vertex(self.x * other.x, self.y * other.y, self.z * other.z)
        else:
            raise ValueError(f"unsupported operand type(s) for *: 'vertex' and '{type(other).__name__}'")

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            return vertex(self.x / other, self.y / other, self.z / other)
        else:
            raise ValueError(f"unsupported operand type(s) for /: 'vertex' and '{type(other).__name__}'")


class triangle(Renderable, EqualityMixin):
    def __init__(self, v1, v2, v3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    def render(self):
        return f"""facet normal 0 0 0
  outer loop
    {self.v1.render()}
    {self.v2.render()}
    {self.v3.render()}
  endloop
endfacet"""

    def renderBinary(self):
        return vertex(0, 0, 0).renderBinary() + \
            self.v1.renderBinary() + \
            self.v2.renderBinary() + \
            self.v3.renderBinary() + \
            bytearray(struct.pack("<h", 0))


def quad(v1, v2, v3, v4):
    return fragment(
        triangle(v1, v2, v3),
        triangle(v1, v3, v4),
    )


class solid(Renderable, EqualityMixin):
    def __init__(self, name, child):
        self.name = name
        self.child = child

    def render(self):
        return f"""solid {self.name}
{self.child.render()}
endsolid {self.name}"""


def planeSubdivisionPoints(numberOfCuts):
    xDeltaVector = vertex(2, 0, 0) / numberOfCuts
    yDeltaVector = vertex(0, 2, 0) / numberOfCuts
    return [
        vertex(-1, -1, 0) + yDeltaVector * y + xDeltaVector * x
        for y in range(numberOfCuts + 1)
        for x in range(numberOfCuts + 1)
    ]


def quadsFromPlaneSubdivisionPoints(points):
    numberOfPointsPerSide = floor(sqrt(len(points)))
    return fragment(*[
        quad(
            points[x + y * numberOfPointsPerSide],
            points[(x + 1) + y * numberOfPointsPerSide],
            points[(x + 1) + (y + 1) * numberOfPointsPerSide],
            points[x + (y + 1) * numberOfPointsPerSide],
        )
        for y in range(numberOfPointsPerSide - 1)
        for x in range(numberOfPointsPerSide - 1)
    ])


def ladderSubdivideQuads(v1, v2, v3, v4, numberOfCuts):
    return fragment(*[
        quad(
            lerp(v1, v2, a, numberOfCuts),
            lerp(v1, v2, a + 1, numberOfCuts),
            lerp(v4, v3, a + 1, numberOfCuts),
            lerp(v4, v3, a, numberOfCuts),
        ) for a in range(numberOfCuts)
    ])


def lerp(v1, v2, numerator, denominator):
    return vertex(
        v1.x + (v2.x - v1.x) * numerator / denominator,
        v1.y + (v2.y - v1.y) * numerator / denominator,
        v1.z + (v2.z - v1.z) * numerator / denominator,
    )


def polarVertex(radius, t, z):
    return vertex(
        cos(radians(t)) * radius,
        sin(radians(t)) * radius,
        z,
    )


def subdividePoints(pointsPerSide, v1, v2, v3):
    xDeltaVector = (v2 - v1) / pointsPerSide
    yDeltaVector = (v3 - v1) / pointsPerSide
    return [
        v1 + xDeltaVector * x + yDeltaVector * y
        for y in range(pointsPerSide + 1)
        for x in range(pointsPerSide + 1 - y)
    ]


def trianglesFromSubdivisionPoints(pointsPerSide, points):
    getPoint = lambda x, y: points[y * ((pointsPerSide - 1) * 2 - y + 5) // 2 + x]

    results = []
    for y in range(pointsPerSide):
        for x in range(pointsPerSide - y):
            results.append(
                triangle(
                    getPoint(x, y),
                    getPoint(x + 1, y),
                    getPoint(x, y + 1),
                )
            )
    for y in range(pointsPerSide - 1):
        for x in range(pointsPerSide - 1 - y):
            results.append(
                triangle(
                    getPoint(x + 1, y),
                    getPoint(x + 1, y + 1),
                    getPoint(x, y + 1),
                )
            )
    return fragment(*results)
