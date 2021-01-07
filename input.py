from typing import Any, Optional
import tcod


def poll_input() -> Optional[tuple[Any, Any]]:
    event_type: str
    event_key: Optional[int] = None

    # if TCOD:
    event_ = next(tcod.event.wait())
    if not event_:
        return None, None
    event_type = event_.type
    if event_type == "KEYDOWN":
        event_key = event_.sym
        if event_.mod & tcod.event.KMOD_SHIFT:
            event_key = ord(chr(event_.sym).upper())

    return event_type, event_key
