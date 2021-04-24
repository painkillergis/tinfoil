from collections import namedtuple
from math import cos, radians, sin


def render(*args):
    return "\n".join(map(renderNode, args))


def renderNode(arg):
    if type(arg) is list:
        return render(*arg)
    elif type(arg) is str:
        return arg
    elif type(arg).__name__ == "vertex":
        return f"vertex {float(arg.x)} {float(arg.y)} {float(arg.z)}"
    elif type(arg).__name__ == "tri":
        return f"""facet normal 0 0 0
  outer loop
    {render(arg.v1)}
    {render(arg.v2)}
    {render(arg.v3)}
  endloop
endfacet"""
    elif type(arg).__name__ == "quad":
        return render([
            triangle(arg.v1, arg.v2, arg.v3),
            triangle(arg.v1, arg.v3, arg.v4),
        ])
    elif type(arg).__name__ == "solid":
        return f"""solid {arg.name}
{render(arg.facets)}
endsolid {arg.name}"""


vertex = namedtuple("vertex", ["x", "y", "z"])

triangle = namedtuple("tri", ["v1", "v2", "v3"])

quad = namedtuple("quad", ["v1", "v2", "v3", "v4"])

solid = namedtuple("solid", ["name", "facets"])


def subdivideQuads(v1, v2, v3, v4, numberOfCuts):
    return [
        ladderSubdivideQuads(quad.v1, quad.v4, quad.v3, quad.v2, numberOfCuts)
        for quad in ladderSubdivideQuads(v1, v2, v3, v4, numberOfCuts)
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
    xDeltaVector = divideVectorByScalar(subtractVectors(v2, v1), pointsPerSide)
    yDeltaVector = divideVectorByScalar(subtractVectors(v3, v1), pointsPerSide)
    results = []
    for y in range(pointsPerSide + 1):
        for x in range(pointsPerSide + 1 - y):
            results.append(
                addVectors(
                    v1,
                    multiplyVectorByScalar(xDeltaVector, x),
                    multiplyVectorByScalar(yDeltaVector, y)
                )
            )
    return results


def divideVectorByScalar(vector, scalar):
    return vertex(vector.x / scalar, vector.y / scalar, vector.z / scalar)


def subtractVectors(v1, v2):
    return vertex(v1.x - v2.x, v1.y - v2.y, v1.z - v2.z)


def addVectors(*vs):
    x = 0
    y = 0
    z = 0
    for v in vs:
        x += v.x
        y += v.y
        z += v.z
    return vertex(x, y, z)


def multiplyVectorByScalar(vector, scalar):
    return vertex(vector.x * scalar, vector.y * scalar, vector.z * scalar)


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
