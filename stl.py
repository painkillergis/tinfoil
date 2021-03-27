def render(*args):
    return "\n".join(
        map(
            lambda arg: render(*arg)
            if type(arg) is list
            else arg,
            args,
        )
    )


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


def rectangle(v1, v2, v3, v4):
    return [
        triangle(v1, v2, v3),
        triangle(v1, v3, v4),
    ]
