import entity
import databases
import game_entities


class Camera(entity.Entity):
    def __init__(
            self,
            x: int,
            y: int,
            game_data: databases.Databases,
            game_entities_: "game_entities.GameEntities"
    ) -> None:
        tile: dict = game_data.tiles["CAMERA"]
        super().__init__(x, y, tile["Name"], tile["Desc"],
                         tile["Blocked"], tile["Character"], tile["Color"], game_entities_)

        self.fov = []

        self._compute_fov()
        self.game_entities.cameras.append(self)

    def _compute_fov(self) -> None:
        pass
