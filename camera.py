import entity


class Camera(entity.Entity):
    def __init__(self, x, y, game_data, game_entities):
        tile = game_data.tiles["CAMERA"]
        super().__init__(x, y, tile["Name"], tile["Desc"],
                         tile["Blocked"], tile["Character"], tile["Color"], game_entities)

        self.fov = []

        self._compute_fov()
        self.game_entities.cameras.append(self)

    def _compute_fov(self):
        pass
