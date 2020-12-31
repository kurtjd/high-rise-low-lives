import entity
import databases
import game_entities


class Door(entity.Entity):
    # ~~~ PRIVATE METHODS ~~~

    def __init__(
            self,
            x: int,
            y: int,
            game_data: databases.Databases,
            game_entities_: "game_entities.GameEntities"
    ) -> None:
        tile: dict = game_data.tiles["DOOR_CLOSED"]
        super().__init__(x, y, tile["Name"], tile["Desc"], tile["Blocked"],
                         tile["Character"], tile["Color"], game_entities_)
        self.game_data: databases.Databases = game_data
        self.opened: bool = False
        self.locked: bool = False
        game_entities_.doors.append(self)

    # ~~~ PUBLIC METHODS ~~~

    # Changes the appearance of the door and makes it no longer blocked.
    def open(self) -> None:
        self.opened = True
        self.blocked = False
        self.graphic = self.game_data.tiles["DOOR_OPEN"]["Character"]
        self.color = self.game_data.tiles["DOOR_OPEN"]["Color"]

    def close(self) -> None:
        self.opened = False
        self.blocked = True
        self.graphic = self.game_data.tiles["DOOR_CLOSED"]["Character"]
        self.color = self.game_data.tiles["DOOR_CLOSED"]["Color"]
