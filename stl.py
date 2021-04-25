import numbers
from abc import ABCMeta, abstractmethod
from math import cos, radians, sin, sqrt, floor


def render(*args):
    if len(args) > 1:
        return "\n".join(map(render, args))

    arg = args[0]
    if type(arg) is list:
        return render(*arg)
    if type(arg) is str:
        return arg
    if isinstance(arg, Renderable):
        return arg.render()
    if isinstance(arg, RenderableAncestor):
        return render(arg.children())


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


class RenderableAncestor:
    __metaclass__ = ABCMeta

    @abstractmethod
    def children(self): raise NotImplementedError


class vertex(Renderable, EqualityMixin):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def render(self):
        return f"vertex {float(self.x)} {float(self.y)} {float(self.z)}"

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
    {render(self.v1)}
    {render(self.v2)}
    {render(self.v3)}
  endloop
endfacet"""


class quad(RenderableAncestor, EqualityMixin):
    def __init__(self, v1, v2, v3, v4):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4

    def children(self):
        return [
            triangle(self.v1, self.v2, self.v3),
            triangle(self.v1, self.v3, self.v4),
        ]


class solid(Renderable, EqualityMixin):
    def __init__(self, name, facets):
        self.name = name
        self.facets = facets

    def render(self):
        return f"""solid {self.name}
{render(self.facets)}
endsolid {self.name}"""


class planeSubdivision(RenderableAncestor, EqualityMixin):
    def __init__(self, v1, v2, v3, v4, numberOfCuts):
        xDeltaVector = (v2 - v1) / numberOfCuts
        yDeltaVector = (v4 - v1) / numberOfCuts
        self.numberOfCuts = numberOfCuts
        self.numberOfPointsPerSide = self.numberOfCuts + 2
        self.points = [
            v1 + yDeltaVector * y + xDeltaVector * x
            for y in range(self.numberOfPointsPerSide)
            for x in range(self.numberOfPointsPerSide)
        ]

    def children(self):
        return [
            quad(
                self.points[x * self.numberOfPointsPerSide + y],
                self.points[(x + 1) * self.numberOfPointsPerSide + y],
                self.points[(x + 1) * self.numberOfPointsPerSide + (y + 1)],
                self.points[x * self.numberOfPointsPerSide + (y + 1)],
            )
            for y in range(self.numberOfCuts)
            for x in range(self.numberOfCuts)
        ]


def ladderSubdivideQuads(v1, v2, v3, v4, numberOfCuts):
    return [
        quad(
            lerp(v1, v2, a, numberOfCuts),
            lerp(v1, v2, a + 1, numberOfCuts),
            lerp(v4, v3, a + 1, numberOfCuts),
            lerp(v4, v3, a, numberOfCuts),
        ) for a in range(numberOfCuts)
    ]


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
    return results
