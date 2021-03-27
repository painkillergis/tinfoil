def render(string):
    return string


def vertex(x, y, z):
    return f"vertex {x} {y} {z}"


def triangle(v1, v2, v3):
    return f"""facet normal 0 0 0
  outer loop
    {v1}
    {v2}
    {v3}
  endloop
endfacet"""
