import json


class Databases:
    def __init__(self) -> None:
        self.npcs: dict = {}
        self.weapons: dict = {}
        self.tiles: dict = {}
        self.colors: dict = {}
        self.throwables: dict = {}
        self.drugs: dict = {}
        self.power_sources: dict = {}
        self.misc_items: dict = {}
        self.ammo: dict = {}

    def load_from_files(self) -> None:
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

        # Throwables
        with open("Data/throwables.dat") as data_file:
            self.throwables = json.load(data_file)

        # Drugs
        with open("Data/drugs.dat") as data_file:
            self.drugs = json.load(data_file)

        # Power Sources
        with open("Data/powersources.dat") as data_file:
            self.power_sources = json.load(data_file)

        # Misc items
        with open("Data/misc_items.dat") as data_file:
            self.misc_items = json.load(data_file)

        # Misc items
        with open("Data/ammo.dat") as data_file:
            self.ammo = json.load(data_file)
