from argparse import ArgumentParser

import numpy
from PIL import Image

from stl import *

parser = ArgumentParser()
parser.add_argument("source")
parser.add_argument("destination")
args = parser.parse_args()

heightmap = numpy.array(Image.open(args.source))
heightmapHeight, heightmapWidth = heightmap.shape


def pipeline(values, *fns):
    for fn in fns:
        values = list(map(fn, values))
    return values


def move(v2):
    return lambda v1: v1 + v2


def scale(operand):
    return lambda v1: v1 * operand


with open(args.destination, "w") as f:
    f.write(
        render(
            solid(
                "plane",
                quadsFromPlaneSubdivisionPoints(
                    pipeline(
                        planeSubdivisionPoints(512),
                        move(vertex(1, 1, 0)),
                        scale(0.5),
                        lambda v: v + vertex(0, 0, heightmap[
                            int(v.x * (heightmapWidth - 1)),
                            int(v.y * (heightmapHeight - 1)),
                        ] / 65533),
                        move(vertex(-0.5, -0.5, 0)),
                        scale(vertex(50, 50, 4)),
                        scale(0.001),
                    )
                ),
            ),
        )
    )
