from __future__ import annotations
import interface
import databases
from .entities import GameEntities
from .entity import Entity


class Tile(Entity):
    """Represents a static tile on the game map."""

    def __init__(
            self,
            x: int,
            y: int,
            name: str,
            desc: str,
            blocked: bool,
            graphic: str,
            color: tuple[int, int, int],
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface,
            cover_percent: int = 0,
            visible: bool = True
    ) -> None:
        super().__init__(
            x,
            y,
            name,
            desc,
            blocked,
            graphic,
            color,
            game_data,
            game_entities_,
            game_interface,
            cover_percent,
            visible
        )

        game_entities_.tiles.append(self)
