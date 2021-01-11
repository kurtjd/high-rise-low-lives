import json


class Databases:
    """Holds all game data and provides methods for working with it."""

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
        """Loads in data from JSON files and assigns to respective dictionaries
        so that other game objects can access the data."""

        # Colors
        with open("data/colors.dat") as data_file:
            self.colors = json.load(data_file)

        # Tiles
        with open("data/tiles.dat") as data_file:
            self.tiles = json.load(data_file)
        # Convert ASCII code of each tile to character.
        for tile in self.tiles:
            self.tiles[tile]["Character"] = chr(self.tiles[tile]["Character"])

        # NPCs
        with open("data/npcs.dat") as data_file:
            self.npcs = json.load(data_file)

        # Weapons
        with open("data/weapons.dat") as data_file:
            self.weapons = json.load(data_file)

        # Throwables
        with open("data/throwables.dat") as data_file:
            self.throwables = json.load(data_file)

        # Drugs
        with open("data/drugs.dat") as data_file:
            self.drugs = json.load(data_file)

        # Power Sources
        with open("data/powersources.dat") as data_file:
            self.power_sources = json.load(data_file)

        # Misc items
        with open("data/misc_items.dat") as data_file:
            self.misc_items = json.load(data_file)

        # Misc items
        with open("data/ammo.dat") as data_file:
            self.ammo = json.load(data_file)
