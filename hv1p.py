from argparse import ArgumentParser
from stl import *

import numpy
from PIL import Image
from math import pi, sin, cos, degrees

parser = ArgumentParser()
parser.add_argument("source")
parser.add_argument("destination")
parser.add_argument("width", type=float)
parser.add_argument("detail", type=int)
args = parser.parse_args()

a = args.width / 4
b = a * sqrt(3)


def modelCoordinatesToUnit(v):
    return vertex((v.x + 2 * a) / (4 * a), (v.y + b) / (2 * b), v.z)


def unitToModelCoordinates(v):
    return vertex(v.x * (4 * a) - 2 * a, v.y * (2 * b) - b, v.z)


def pipeline(values, *fns):
    for fn in fns:
        values = list(map(fn, values))
    return values


def move(v2):
    return lambda v1: v1 + v2


def scale(operand):
    return lambda v1: v1 * operand


def unpack(_lambda):
    def unpacker(tuple):
        return _lambda(*tuple)

    return unpacker


tiles = [
    triangle(
        vertex(0, 0, 0),
        vertex(2 * a, 0, 0),
        vertex(a, b, 0),
    ),
    triangle(
        vertex(-a, b, 0),
        vertex(0, 0, 0),
        vertex(a, b, 0),
    ),
    triangle(
        vertex(-2 * a, 0, 0),
        vertex(0, 0, 0),
        vertex(-a, b, 0),
    ),
    triangle(
        vertex(-2 * a, 0, 0),
        vertex(-a, -b, 0),
        vertex(0, 0, 0),
    ),
    triangle(
        vertex(-a, -b, 0),
        vertex(a, -b, 0),
        vertex(0, 0, 0),
    ),
    triangle(
        vertex(0, 0, 0),
        vertex(a, -b, 0),
        vertex(2 * a, 0, 0),
    ),
]


def log(args):
    print(cos(-args[0] * pi / 3))
    return args


def hv1p():
    heightmap = numpy.array(Image.open(args.source))
    heightmapHeight, heightmapWidth = heightmap.shape
    tops = pipeline(
        enumerate(tiles),
        unpack(lambda index, tile: pipeline(
            subdividePoints(
                args.detail,
                tile.v1,
                tile.v2,
                tile.v3,
            ),
            modelCoordinatesToUnit,
            scale(vertex(heightmapWidth - 1, heightmapHeight - 1, 1)),
            lambda v: vertex(v.x, v.y, heightmap[int(v.x), int(v.y)]),
            scale(vertex(1 / (heightmapWidth - 1), 1 / (heightmapHeight - 1), 1)),
            unitToModelCoordinates,
            move(
                vertex(
                    sin((1 - index) * pi / 3),
                    cos((1 - index) * pi / 3),
                    0,
                ) * a / 4,
            ),
        ))
    )

    bottoms = pipeline(
        enumerate(tiles),
        unpack(lambda index, tile: pipeline(
            subdividePoints(args.detail, tile.v1, tile.v2, tile.v3),
            move(
                vertex(
                    sin((1 - index) * pi / 3),
                    cos((1 - index) * pi / 3),
                    0,
                ) * a / 4,
            ),
        ))
    )

    def wall1(top, bottom):
        topEdges = top[0:args.detail + 1]
        bottomEdges = bottom[0:args.detail + 1]
        return fragment(*[
            quad(
                bottomEdges[i],
                bottomEdges[i + 1],
                topEdges[i + 1],
                topEdges[i],
            ) for i in range(len(topEdges) - 1)
        ])

    def wall2(top, bottom):
        t = lambda x: int(x * (x + 1) / 2)

        topEdges = [top[-t(i + 1)] for i in range(args.detail + 1)]
        bottomEdges = [bottom[-t(i + 1)] for i in range(args.detail + 1)]
        return fragment(*[
            quad(
                bottomEdges[i],
                bottomEdges[i + 1],
                topEdges[i + 1],
                topEdges[i],
            ) for i in range(len(topEdges) - 1)
        ])

    def wall3(top, bottom):
        t = lambda x: int(x * (x + 1) / 2)

        topEdges = [top[-1 - t(i)] for i in range(args.detail + 1)]
        bottomEdges = [bottom[-1 - t(i)] for i in range(args.detail + 1)]
        return fragment(*[
            quad(
                bottomEdges[i],
                bottomEdges[i + 1],
                topEdges[i + 1],
                topEdges[i],
            ) for i in range(len(topEdges) - 1)
        ])

    models = pipeline(
        zip(tops, bottoms),
        unpack(lambda top, bottom: fragment(
            trianglesFromSubdivisionPoints(args.detail, top),
            trianglesFromSubdivisionPoints(args.detail, bottom, True),
            wall1(top, bottom),
            wall2(top, bottom),
            wall3(top, bottom),
        )),
    )

    return [solid("solid", fragment(*models))]


for solid in hv1p():
    with open(args.destination.replace("%s", solid.name), 'w') as f:
        f.write(render(solid))
