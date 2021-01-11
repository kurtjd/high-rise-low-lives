from __future__ import annotations
import databases
import interface
from .entities import GameEntities
from .entity import Entity


class Camera(Entity):
    """Represents a security camera."""

    def __init__(
            self,
            x: int,
            y: int,
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface
    ) -> None:
        tile_: dict = game_data.tiles["CAMERA"]
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
            game_interface
        )

        self.radius: int = 4
        self.fov: list[tuple[int, int]] = self.compute_fov(self.radius)

        self.triggered: bool = False  # If the player triggered this camera to sound alarms

        self.game_entities.cameras.append(self)

    def update(self, game_time: int) -> None:
        """Updates the camera."""

        if not self.triggered:
            # Check if player is within FOV, if so sound alarms by making a lot of noise.
            # Eventually also do stealth check.
            for point in self.fov:
                if point[0] == self.game_entities.player.x and point[1] == self.game_entities.player.y:
                    self.triggered = True
                    self.game_interface.message_box.add_msg(
                        f"You've been spotted! Alarms sounded!", self.game_data.colors["SYS_MSG"]
                    )
                    break

        if self.triggered:
            self.make_noise(999)
