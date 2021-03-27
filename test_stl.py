from stl import *
from pytest import approx


def test_vertex():
    assert render(vertex(1, 2, 3)) == "vertex 1.0 2.0 3.0"


def test_triangle():
    assert render(
        triangle(
            vertex(1, 2, 3),
            vertex(4, 5, 6),
            vertex(7, 8, 9),
        ),
    ) == """facet normal 0 0 0
  outer loop
    vertex 1.0 2.0 3.0
    vertex 4.0 5.0 6.0
    vertex 7.0 8.0 9.0
  endloop
endfacet"""


def test_quad():
    assert render(quad("a", "b", "c", "d")) == render(
        triangle("a", "b", "c"),
        triangle("a", "c", "d"),
    )


def test_subdivideQuads():
    assert render(
        subdivideQuads(
            vertex(0, 0, 0),
            vertex(2, 0, 0),
            vertex(2, 2, 0),
            vertex(0, 2, 0),
            2,
        ),
    ) == render(
        quad(
            vertex(0, 0, 0),
            vertex(1, 0, 0),
            vertex(1, 2, 0),
            vertex(0, 2, 0),
        ),
        quad(
            vertex(1, 0, 0),
            vertex(2, 0, 0),
            vertex(2, 2, 0),
            vertex(1, 2, 0),
        ),
    )


def test_polarVertex():
    assert polarVertex(1, 0, 128) == vertex(1, 0, 128)
    assert polarVertex(2, 90, 64) == vertex(approx(0), 2, 64)
    assert polarVertex(4, 180, 32) == vertex(-4, approx(0), 32)
    assert polarVertex(8, 270, 16) == vertex(approx(0), -8, 16)
