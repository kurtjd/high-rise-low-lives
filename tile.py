from __future__ import annotations
import entities
import interface
import databases
import entity


class Tile(entity.Entity):
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
            game_entities_: entities.GameEntities,
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
