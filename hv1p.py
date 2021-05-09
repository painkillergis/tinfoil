from argparse import ArgumentParser
from math import pi, sin, cos

import numpy
from PIL import Image

from stl import *

parser = ArgumentParser()
parser.add_argument("source")
parser.add_argument("destination")
parser.add_argument("width", type=float)
parser.add_argument("detail", type=int)
parser.add_argument("--vertical-detail", type=int, default=1)
parser.add_argument("--multiple-files", action='store_true')
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

    def wall(topEdge, bottomEdge):
        return fragment(*[
            quad(
                lerp(bottomEdge[x], topEdge[x], y, args.vertical_detail),
                lerp(bottomEdge[x + 1], topEdge[x + 1], y, args.vertical_detail),
                lerp(bottomEdge[x + 1], topEdge[x + 1], y + 1, args.vertical_detail),
                lerp(bottomEdge[x], topEdge[x], y + 1, args.vertical_detail),
            )
            for y in range(args.vertical_detail)
            for x in range(len(topEdge) - 1)
        ])

    def t(x):
        return int(x * (x + 1) / 2)

    models = pipeline(
        zip(tops, bottoms),
        unpack(lambda top, bottom: fragment(
            trianglesFromSubdivisionPoints(args.detail, top),
            trianglesFromSubdivisionPoints(args.detail, bottom, True),
            wall(
                top[0:args.detail + 1],
                bottom[0:args.detail + 1],
            ),
            wall(
                [top[-t(i + 1)] for i in range(args.detail + 1)],
                [bottom[-t(i + 1)] for i in range(args.detail + 1)],
            ),
            wall(
                [top[-1 - t(args.detail - i)] for i in range(args.detail + 1)],
                [bottom[-1 - t(args.detail - i)] for i in range(args.detail + 1)],
            ),
        )),
    )

    if args.multiple_files:
        return [solid(str(index), model) for index, model in enumerate(models)]
    else:
        return [solid("0", fragment(*models))]


for solid in hv1p():
    with open(args.destination.replace("%s", solid.name), 'w') as f:
        f.write(render(solid))
