from __future__ import annotations
import databases
import interface
import entities
import actor
import ai


class Turret(actor.Actor):
    """Represents a turret."""

    def __init__(
            self,
            x: int,
            y: int,
            game_data: databases.Databases,
            game_entities_: entities.GameEntities,
            game_interface: interface.Interface
    ):
        self.turret_data: dict = game_data.npcs["TURRET"]
        self.disabled: bool = False
        self.friendly_fire: bool = False

        super().__init__(
            self.turret_data["Name"],
            self.turret_data["Race"],
            self.turret_data["Class"],
            self.turret_data["Description"],
            x,
            y,
            100,
            self.turret_data["Muscle"],
            self.turret_data["Smarts"],
            self.turret_data["Reflexes"],
            self.turret_data["Wits"],
            self.turret_data["Grit"],
            ai.turret,
            self.turret_data["Graphic"],
            self.turret_data["Color"],
            game_data,
            game_entities_,
            game_interface
        )

        self.game_entities.turrets.append(self)
