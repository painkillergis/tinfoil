from stl import *


def test_render_vertex():
    assert render(vertex(1, 2, 3)) == "vertex 1 2 3"


def test_vertex():
    assert vertex(1, 2, 3) != vertex(3, 2, 1)


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