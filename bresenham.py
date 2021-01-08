import tcod


def bresenham(point1: tuple[int, int], point2: tuple[int, int]) -> list[tuple[int, int]]:
    # if TCOD:
    return tcod.los.bresenham(point1, point2).tolist()[:]
