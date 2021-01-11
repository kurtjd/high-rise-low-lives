from __future__ import annotations
import databases
import interface
from .entities import GameEntities
from .tile import Tile


class Vent(Tile):
    """Represents a vent."""

    def __init__(
            self,
            x: int,
            y: int,
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface,
            entrance: bool = False
    ) -> None:
        self.entrance: bool = entrance  # Whether or not this is an entrance vent.
        visible: bool = True
        tile_: dict

        if self.entrance:
            tile_ = game_data.tiles["VENT_ENTER"]
        else:
            tile_ = game_data.tiles["VENT"]
            visible = False

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
            visible
        )

        game_entities_.vents.append(self)
