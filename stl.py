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


vertex = namedtuple("vertex", ["x", "y", "z"])

triangle = namedtuple("tri", ["v1", "v2", "v3"])


def quad(v1, v2, v3, v4):
    return [
        triangle(v1, v2, v3),
        triangle(v1, v3, v4),
    ]


def subdivideQuads(v1, v2, v3, v4, numberOfCuts):
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
