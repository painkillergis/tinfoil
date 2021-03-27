from stl import *
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("destination")
args = parser.parse_args()

facets = render(
    subdivide(
        vertex(-1, 0, 0),
        vertex(1, 0, 0),
        vertex(1, 1, 0),
        vertex(-1, 1, 0),
        72,
    ),
)

with open(args.destination, "w") as f:
    f.write(f"""solid sample
{facets}
endsolid sample""")
