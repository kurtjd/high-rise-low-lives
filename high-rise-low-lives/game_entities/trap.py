from __future__ import annotations
import interface
import databases
from .entities import GameEntities
from .entity import Entity


class Trap(Entity):
    """Represents a trap."""

    def __init__(
            self,
            x: int,
            y: int,
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface
    ) -> None:
        tile_: dict = game_data.tiles["TRAP"]

        super().__init__(
            x,
            y,
            tile_["Name"],
            tile_["Desc"],
            tile_["Blocked"],
            tile_["Character"],
            tile_["Color"],
            game_data,
            game_entities_,
            game_interface,
            tile_["Cover Percent"],
            False
        )

        self.triggered: bool = False

        self.game_entities.traps.append(self)

    def trigger(self) -> None:
        """Triggers the trap and performs some action."""

        if self.triggered:
            return

        # Later implement different nasty effects such as shocking the player.
        self.triggered = True
        self.visible = True
