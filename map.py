from entity import Entity
import door
import globals


# Will eventually create a procedurally-generated map.
def generate_map(width, height):
    game_map = [[Entity(x, y, globals.tiles["FLOOR"].tile, globals.tiles["FLOOR"].color)
                 for x in range(width)] for y in range(height)]

    return game_map


# Converts a character from a map file into a game entity.
def char_to_entity(char, x, y):
    if char == '.':
        tile = globals.tiles["FLOOR"]
        entity = Entity(x, y, tile["Character"], tile["Color"], tile["Blocked"])
    elif char == '-':
        tile = globals.tiles["WALL_HORIZ"]
        entity = Entity(x, y, tile["Character"], tile["Color"], tile["Blocked"])
    elif char == '|':
        tile = globals.tiles["WALL_VERT"]
        entity = Entity(x, y, tile["Character"], tile["Color"], tile["Blocked"])
    elif char == '1':
        tile = globals.tiles["WALL_COR_TL"]
        entity = Entity(x, y, tile["Character"], tile["Color"], tile["Blocked"])
    elif char == '2':
        tile = globals.tiles["WALL_COR_TR"]
        entity = Entity(x, y, tile["Character"], tile["Color"], tile["Blocked"])
    elif char == '3':
        tile = globals.tiles["WALL_COR_BR"]
        entity = Entity(x, y, tile["Character"], tile["Color"], tile["Blocked"])
    elif char == '4':
        tile = globals.tiles["WALL_COR_BL"]
        entity = Entity(x, y, tile["Character"], tile["Color"], tile["Blocked"])
    elif char == '#':
        tile = globals.tiles["HALL"]
        entity = Entity(x, y, tile["Character"], tile["Color"], tile["Blocked"])
    elif char == '+':
        tile = globals.tiles["DOOR_CLOSED"]
        entity = door.Door(x, y, tile["Character"], tile["Color"], tile["Blocked"])
    else:
        tile = globals.tiles["BLANK"]
        entity = Entity(x, y, tile["Character"], tile["Color"], tile["Blocked"])

    return entity


# Reads a map from a text file.
def read_map(file):
    game_map = []
    map_file = open(file)
    map_lines = map_file.readlines()

    for y in enumerate(map_lines):
        game_map.append([])
        for x in enumerate(y[1]):
            entity = char_to_entity(x[1], x[0], y[0])
            game_map[y[0]].append(entity)

    return game_map
