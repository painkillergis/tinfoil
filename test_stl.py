from stl import *


def test_render_vertex():
    assert render(vertex(1, 2, 3)) == "vertex 1 2 3"


def test_render_triangle():
    assert render(
        triangle(
            vertex(1, 2, 3),
            vertex(4, 5, 6),
            vertex(7, 8, 9),
        ),
    ) == """facet normal 0 0 0
  outer loop
    vertex 1 2 3
    vertex 4 5 6
    vertex 7 8 9
  endloop
endfacet"""


def test_rectangle():
    assert render(rectangle("a", "b", "c", "d")) == render(
        triangle("a", "b", "c"),
        triangle("a", "c", "d"),
    )
