from typing import Any, Optional


def render(
        surface: Any,
        graphic: Any,
        x: int,
        y: int,
        fgcolor: Optional[tuple[int, int, int]] = None,
        bgcolor: Optional[tuple[int, int, int]] = None
) -> None:
    """ Generic render function which will decide which specific render function to
        call depending on which mode the game is in. """
    # if TCOD:
    surface.print(x=x, y=y, string=graphic, fg=fgcolor, bg=bgcolor)


def clear_surface(surface: Any) -> None:
    """ Generic clear surface function which will decide which specific clear function to
        call depending on which mode the game is in. """
    # if TCOD:
    surface.clear()


def present_surface(window: Any, surface: Any) -> None:
    """ Generic present surface function which will decide which specific present function to
            call depending on which mode the game is in. """
    # if TCOD:
    window.present(surface)
