from stl import *
from argparse import ArgumentParser
from math import sqrt

parser = ArgumentParser()
parser.add_argument("source")
parser.add_argument("destination")
args = parser.parse_args()

radius = sqrt(3) * 2 / 3
height = 0.25

contents = render(
    solid(
        "sample",
        [
            [
                ladderSubdivideQuads(
                    polarVertex(radius, t, -height / 2),
                    polarVertex(radius, t + 120, -height / 2),
                    polarVertex(radius, t + 120, height / 2),
                    polarVertex(radius, t, height / 2),
                    72,
                ) for t in range(0, 360, 120)
            ],
            triangle(*[polarVertex(radius, t, -height / 2) for t in range(0, 360, 120)]),
            trianglesFromSubdivisionPoints(
                10,
                sampleZ(
                    args.source,
                    subdividePoints(
                        10,
                        *[polarVertex(radius, t, height / 2) for t in range(0, 360, 120)],
                    ),
                )
            ),
        ]
    )
)

with open(args.destination, "w") as f:
    f.write(contents)
