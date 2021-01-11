import databases
import interface
import game_entities.entities
import game_entities.entity
import game_entities.tile
import game_entities.vent
import game_entities.door


class Map:
    """Represents a game map.
    Right now this is pretty useless other than the read_map method, because a map is just a collection of entities
    and the game_entities list holds all of those."""

    def __init__(
            self,
            game_data: databases.Databases,
            game_entities_: game_entities.entities.GameEntities,
            game_interface: interface.Interface
    ) -> None:
        # self.map = []
        self.game_data: databases.Databases = game_data
        self.game_entities: game_entities.entities.GameEntities = game_entities_
        self.game_interface: interface.Interface = game_interface

    def _char_to_entity(self, char: str, x: int, y: int) -> game_entities.entity.Entity:
        """Converts a character from a map file into a game entity."""

        tiles: dict = {
            '.': self.game_data.tiles["FLOOR"],
            '-': self.game_data.tiles["WALL_HORIZ"],
            '|': self.game_data.tiles["WALL_VERT"],
            '1': self.game_data.tiles["WALL_COR_TL"],
            '2': self.game_data.tiles["WALL_COR_TR"],
            '3': self.game_data.tiles["WALL_COR_BR"],
            '4': self.game_data.tiles["WALL_COR_BL"],
            '#': self.game_data.tiles["HALL"],
            ':': self.game_data.tiles["VENT_ENTER"],
            '+': self.game_data.tiles["DOOR_CLOSED"],
            '_': self.game_data.tiles["DESK"]
        }
        new_tile: dict = tiles.get(char, self.game_data.tiles["BLANK"])

        if char == '+':
            new_entity = game_entities.door.Door(x, y, self.game_data, self.game_entities, self.game_interface)
        elif char == ':':
            new_entity = game_entities.vent.Vent(x, y, self.game_data, self.game_entities, self.game_interface, True)
        elif char == '"':
            new_entity = game_entities.vent.Vent(x, y, self.game_data, self.game_entities, self.game_interface)
        else:
            new_entity = game_entities.tile.Tile(
                x,
                y,
                new_tile["Name"],
                new_tile["Desc"],
                new_tile["Blocked"],
                new_tile["Character"],
                new_tile["Color"],
                self.game_data,
                self.game_entities,
                self.game_interface,
                new_tile["Cover Percent"]
            )
        return new_entity

    def read_map(self, file: str) -> None:
        """Reads a map from a text file."""

        map_file = open(file)
        map_lines = map_file.readlines()

        for y in enumerate(map_lines):
            # self.map.append([])
            for x in enumerate(y[1]):
                if x[1] != '\n':
                    # new_entity =
                    self._char_to_entity(x[1], x[0], y[0])
                    # self.map[y[0]].append(new_entity)
