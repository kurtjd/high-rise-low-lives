import databases
import entities


class Map:
    def __init__(self, game_data: databases.Databases) -> None:
        # self.map = []
        self.game_data: databases.Databases = game_data

    # Converts a character from a map file into a game entity.
    def _char_to_entity(
            self,
            char: str,
            x: int,
            y: int,
            entities_: entities.GameEntities
    ) -> entities.Entity:
        new_tile: dict
        if char == '.':
            new_tile = self.game_data.tiles["FLOOR"]
        elif char == '-':
            new_tile = self.game_data.tiles["WALL_HORIZ"]
        elif char == '|':
            new_tile = self.game_data.tiles["WALL_VERT"]
        elif char == '1':
            new_tile = self.game_data.tiles["WALL_COR_TL"]
        elif char == '2':
            new_tile = self.game_data.tiles["WALL_COR_TR"]
        elif char == '3':
            new_tile = self.game_data.tiles["WALL_COR_BR"]
        elif char == '4':
            new_tile = self.game_data.tiles["WALL_COR_BL"]
        elif char == '#':
            new_tile = self.game_data.tiles["HALL"]
        elif char == ':':
            new_tile = self.game_data.tiles["VENT_ENTER"]
        elif char == '"':
            new_tile = self.game_data.tiles["VENT"]
        elif char == '+':
            new_tile = self.game_data.tiles["DOOR_CLOSED"]
        else:
            new_tile = self.game_data.tiles["BLANK"]

        if char == '+':
            new_entity = entities.Door(x, y, self.game_data, entities_)
        elif char == ':':
            new_entity = entities.Vent(x, y, self.game_data, entities_, True)
        elif char == '"':
            new_entity = entities.Vent(x, y, self.game_data, entities_)
        else:
            new_entity = entities.Tile(x, y, new_tile["Name"], new_tile["Desc"], new_tile["Blocked"],
                                       new_tile["Character"], new_tile["Color"], entities_)
        return new_entity

    # Reads a map from a text file.
    def read_map(self, file: str, entities_: entities.GameEntities) -> None:
        map_file = open(file)
        map_lines = map_file.readlines()

        for y in enumerate(map_lines):
            # self.map.append([])
            for x in enumerate(y[1]):
                if x[1] != '\n':
                    # new_entity =
                    self._char_to_entity(x[1], x[0], y[0], entities_)
                    # self.map[y[0]].append(new_entity)
