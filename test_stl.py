from pytest import approx

from stl import *


def flatten(args):
    result = []
    for arg in args:
        if type(arg) is list:
            result += flatten(arg)
        else:
            result.append(arg)
    return result


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


def test_solid():
    assert render(solid("something", ["facets"])) == """solid something
facets
endsolid something"""


def test_ladderSubdivideQuads():
    assert render(
        ladderSubdivideQuads(
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


def test_quadSubdivision():
    assert flatten(
        quadSubdivision(
            vertex(0, 0, 0),
            vertex(2, 0, 0),
            vertex(2, 2, 0),
            vertex(0, 2, 0),
            2,
        ).children()
    ) == [
               quad(
                   vertex(0, 0, 0),
                   vertex(0, 1, 0),
                   vertex(1, 1, 0),
                   vertex(1, 0, 0),
               ),
               quad(
                   vertex(0, 1, 0),
                   vertex(0, 2, 0),
                   vertex(1, 2, 0),
                   vertex(1, 1, 0),
               ),
               quad(
                   vertex(1, 0, 0),
                   vertex(1, 1, 0),
                   vertex(2, 1, 0),
                   vertex(2, 0, 0),
               ),
               quad(
                   vertex(1, 1, 0),
                   vertex(1, 2, 0),
                   vertex(2, 2, 0),
                   vertex(2, 1, 0),
               ),
           ]


def test_polarVertex():
    assert polarVertex(1, 0, 128) == vertex(1, 0, 128)
    assert polarVertex(2, 90, 64) == vertex(approx(0), 2, 64)
    assert polarVertex(4, 180, 32) == vertex(-4, approx(0), 32)
    assert polarVertex(8, 270, 16) == vertex(approx(0), -8, 16)


def test_subdividePoints():
    assert subdividePoints(
        3,
        vertex(0, 0, 1),
        vertex(3, 0, 1),
        vertex(0, 3, 1),
    ) == [
               vertex(0, 0, 1),
               vertex(1, 0, 1),
               vertex(2, 0, 1),
               vertex(3, 0, 1),
               vertex(0, 1, 1),
               vertex(1, 1, 1),
               vertex(2, 1, 1),
               vertex(0, 2, 1),
               vertex(1, 2, 1),
               vertex(0, 3, 1),
           ]


def test_trianglesFromSubdivisionPoints():
    assert trianglesFromSubdivisionPoints(
        3,
        [
            vertex(0, 0, 1),
            vertex(1, 0, 1),
            vertex(2, 0, 1),
            vertex(3, 0, 1),
            vertex(0, 1, 1),
            vertex(1, 1, 1),
            vertex(2, 1, 1),
            vertex(0, 2, 1),
            vertex(1, 2, 1),
            vertex(0, 3, 1),
        ],
    ) == [
               triangle(
                   vertex(0, 0, 1),
                   vertex(1, 0, 1),
                   vertex(0, 1, 1),
               ),
               triangle(
                   vertex(1, 0, 1),
                   vertex(2, 0, 1),
                   vertex(1, 1, 1),
               ),
               triangle(
                   vertex(2, 0, 1),
                   vertex(3, 0, 1),
                   vertex(2, 1, 1),
               ),
               triangle(
                   vertex(0, 1, 1),
                   vertex(1, 1, 1),
                   vertex(0, 2, 1),
               ),
               triangle(
                   vertex(1, 1, 1),
                   vertex(2, 1, 1),
                   vertex(1, 2, 1),
               ),
               triangle(
                   vertex(0, 2, 1),
                   vertex(1, 2, 1),
                   vertex(0, 3, 1),
               ),
               triangle(
                   vertex(1, 0, 1),
                   vertex(1, 1, 1),
                   vertex(0, 1, 1),
               ),
               triangle(
                   vertex(2, 0, 1),
                   vertex(2, 1, 1),
                   vertex(1, 1, 1),
               ),
               triangle(
                   vertex(1, 1, 1),
                   vertex(1, 2, 1),
                   vertex(0, 2, 1),
               ),
           ]
