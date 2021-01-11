from enum import Enum, auto
from typing import Optional, Union
import tcod


class EventType(Enum):
    """Generic constants for the type of input event, ie: key press, mouse move, user quit, etc."""

    KEYDOWN = auto(),
    QUIT = auto()


class Key(Enum):
    """Generic constants for keys associated with a keypress the game can use."""

    CTRL_C = auto(),
    ENTER = auto(),
    ESCAPE = auto(),
    UP = auto(),
    RIGHT = auto(),
    LEFT = auto(),
    DOWN = auto(),
    COMMA = auto(),
    PERIOD = auto(),
    MINUS = auto()


def poll_input() -> tuple[EventType, Optional[Union[Key, str]]]:
    """Generic input poller that returns either a character if keys a-z were pressed
    or a corresponding Key if anything else was pressed for the FSM to handle."""

    event_type: EventType
    event_key: Optional[Union[Key, str]] = None

    # if TCOD:
    # Convert tcod specifics to generics
    events: dict = {
        "KEYDOWN": EventType.KEYDOWN,
        "QUIT": EventType.QUIT
    }
    keys: dict = {
        tcod.event.K_RETURN: Key.ENTER,
        tcod.event.K_ESCAPE: Key.ESCAPE,
        tcod.event.K_UP: Key.UP,
        tcod.event.K_DOWN: Key.DOWN,
        tcod.event.K_RIGHT: Key.RIGHT,
        tcod.event.K_LEFT: Key.LEFT,
        tcod.event.K_COMMA: Key.COMMA,
        tcod.event.K_PERIOD: Key.PERIOD,
        tcod.event.K_MINUS: Key.MINUS
    }

    event_ = next(tcod.event.wait())

    event_type = events.get(event_.type)
    if event_type == EventType.KEYDOWN:
        event_key = keys.get(event_.sym)

        # If key is a-z return the actual character instead of a Key.
        if tcod.event.K_a <= event_.sym <= tcod.event.K_z:
            event_key = chr(int(event_.sym))

            # If shift was held while pressing letter key, then capitalize it.
            if event_.mod & tcod.event.KMOD_SHIFT:
                event_key = event_key.upper()

            # Check for ctrl key modifiers.
            elif event_.mod & tcod.event.KMOD_CTRL:
                if event_.sym == tcod.event.K_c:
                    event_key = Key.CTRL_C

    return event_type, event_key
