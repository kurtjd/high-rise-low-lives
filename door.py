import entity


class Door(entity.Entity):
    # ~~~ PRIVATE METHODS ~~~

    def __init__(self, x, y, game_data, game_entities):
        tile = game_data.tiles["DOOR_CLOSED"]
        super().__init__(x, y, tile["Name"], tile["Desc"], tile["Blocked"],
                         tile["Character"], tile["Color"], game_entities)
        self.game_data = game_data
        self.opened = False
        self.locked = False
        game_entities.doors.append(self)

    # ~~~ PUBLIC METHODS ~~~

    # Changes the appearance of the door and makes it no longer blocked.
    def open(self):
        self.opened = True
        self.blocked = False
        self.graphic = self.game_data.tiles["DOOR_OPEN"]["Character"]
        self.color = self.game_data.tiles["DOOR_OPEN"]["Color"]

    def close(self):
        self.opened = False
        self.blocked = True
        self.graphic = self.game_data.tiles["DOOR_CLOSED"]["Character"]
        self.color = self.game_data.tiles["DOOR_CLOSED"]["Color"]
