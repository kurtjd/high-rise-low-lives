import entity
import door


class Map:
    def __init__(self, game_data):
        self.map = []
        self.game_data = game_data

    # Converts a character from a map file into a game entity.
    def __char_to_entity(self, char, x, y, game_entities):
        if char == '.':
            tile = self.game_data.tiles["FLOOR"]
        elif char == '-':
            tile = self.game_data.tiles["WALL_HORIZ"]
        elif char == '|':
            tile = self.game_data.tiles["WALL_VERT"]
        elif char == '1':
            tile = self.game_data.tiles["WALL_COR_TL"]
        elif char == '2':
            tile = self.game_data.tiles["WALL_COR_TR"]
        elif char == '3':
            tile = self.game_data.tiles["WALL_COR_BR"]
        elif char == '4':
            tile = self.game_data.tiles["WALL_COR_BL"]
        elif char == '#':
            tile = self.game_data.tiles["HALL"]
        elif char == '+':
            tile = self.game_data.tiles["DOOR_CLOSED"]
        else:
            tile = self.game_data.tiles["BLANK"]

        if char == '+':
            new_entity = door.Door(x, y, tile["Blocked"], tile["Character"], tile["Color"],
                                   self.game_data, game_entities)
        else:
            new_entity = entity.Entity(x, y, tile["Blocked"], tile["Character"], tile["Color"], game_entities)
        return new_entity

    # Reads a map from a text file.
    def read_map(self, file, game_entities):
        map_file = open(file)
        map_lines = map_file.readlines()

        for y in enumerate(map_lines):
            self.map.append([])
            for x in enumerate(y[1]):
                if x[1] != '\n':
                    new_entity = self.__char_to_entity(x[1], x[0], y[0], game_entities)
                    self.map[y[0]].append(new_entity)
