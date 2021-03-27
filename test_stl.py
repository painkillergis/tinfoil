from stl import *


def test_render_vertex():
    assert render(vertex(1, 2, 3)) == "vertex 1 2 3"
