from stl import *
from argparse import ArgumentParser
from math import sqrt

parser = ArgumentParser()
parser.add_argument("destination")
args = parser.parse_args()

radius = sqrt(3) * 2 / 3
height = 0.25

facets = render(
    subdivide(
        polarVertex(radius, 0, -height / 2),
        polarVertex(radius, 120, -height / 2),
        polarVertex(radius, 120, height / 2),
        polarVertex(radius, 0, height / 2),
        72,
    ),
)

with open(args.destination, "w") as f:
    f.write(f"""solid sample
{facets}
endsolid sample""")
