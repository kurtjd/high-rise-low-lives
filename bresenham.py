import tcod


def bresenham(point1: tuple[int, int], point2: tuple[int, int]) -> list[tuple[int, int]]:
    """Returns a list of points along a line between two grid cells by using the bresenham algorithm."""

    # if TCOD:
    return tcod.los.bresenham(point1, point2).tolist()[:]
