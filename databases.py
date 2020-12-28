import json


class Databases:
    def __init__(self):
        # A database of NPCs
        self.npcs = None

        # A database of weapons
        self.weapons = None

        # A database of tiles
        self.tiles = None

        # A database of colors
        self.colors = None

    def load_from_files(self):
        # Colors
        with open("Data/colors.dat") as data_file:
            self.colors = json.load(data_file)

        # Tiles
        with open("Data/tiles.dat") as data_file:
            self.tiles = json.load(data_file)
        # Convert ASCII code of each tile to character.
        for tile in self.tiles:
            self.tiles[tile]["Character"] = chr(self.tiles[tile]["Character"])

        # NPCs
        with open("Data/npcs.dat") as data_file:
            self.npcs = json.load(data_file)

        # Weapons
        with open("Data/weapons.dat") as data_file:
            self.weapons = json.load(data_file)
