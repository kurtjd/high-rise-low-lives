import tile
import door


class Map:
    def __init__(self, game_data):
        self.map = []
        self.game_data = game_data

    # Converts a character from a map file into a game entity.
    def _char_to_entity(self, char, x, y, game_entities):
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
        elif char == '+':
            new_tile = self.game_data.tiles["DOOR_CLOSED"]
        else:
            new_tile = self.game_data.tiles["BLANK"]

        if char == '+':
            new_entity = door.Door(x, y, self.game_data, game_entities)
        else:
            new_entity = tile.Tile(x, y, new_tile["Name"], new_tile["Desc"], new_tile["Blocked"],
                                   new_tile["Character"], new_tile["Color"], game_entities)
        return new_entity

    # Reads a map from a text file.
    def read_map(self, file, game_entities):
        map_file = open(file)
        map_lines = map_file.readlines()

        for y in enumerate(map_lines):
            self.map.append([])
            for x in enumerate(y[1]):
                if x[1] != '\n':
                    new_entity = self._char_to_entity(x[1], x[0], y[0], game_entities)
                    self.map[y[0]].append(new_entity)
