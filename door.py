from __future__ import annotations
import entities
import interface
import databases
import entity


class Door(entity.Entity):
    """Represents a door"""

    def __init__(
            self,
            x: int,
            y: int,
            game_data: databases.Databases,
            game_entities_: entities.GameEntities,
            game_interface: interface.Interface
    ) -> None:
        tile_: dict = game_data.tiles["DOOR_CLOSED"]

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
            tile_["Cover Percent"]
        )
        self.opened: bool = False
        self.locked: bool = False

        game_entities_.doors.append(self)

    def open(self) -> None:
        """Changes the appearance of the door and makes it no longer blocked."""

        self.opened = True
        self.blocked = False
        self.graphic = self.game_data.tiles["DOOR_OPEN"]["Character"]
        self.color = self.game_data.tiles["DOOR_OPEN"]["Color"]
        self.cover_percent = self.game_data.tiles["DOOR_OPEN"]["Cover Percent"]

    def close(self) -> None:
        """Changes the appearance of the door and makes it blocked."""

        self.opened = False
        self.blocked = True
        self.graphic = self.game_data.tiles["DOOR_CLOSED"]["Character"]
        self.color = self.game_data.tiles["DOOR_CLOSED"]["Color"]
        self.cover_percent = self.game_data.tiles["DOOR_CLOSED"]["Cover Percent"]
