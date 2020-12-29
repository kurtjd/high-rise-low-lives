import tcod
import ai
from interface import Interface
from map import Map
from actor import Actor
from player import Player
from item_entity import ItemEntity
from weapon import Weapon
from databases import Databases
from gamefsm import GameFSM
from game_entities import GameEntities


# Initializes tcod and returns a window and console.
def init_tcod():
    # Initialize tcod and game console
    tileset = tcod.tileset.load_tilesheet("Tilesets/tileset.png", 32, 8, tcod.tileset.CHARMAP_TCOD)
    window = tcod.context.new_terminal(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        tileset=tileset,
        title="High-Rise: Low-Lives",
        vsync=True
    )
    console = tcod.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order='F')

    return (window, console)


# Initializes the player
def init_player(game_data, game_entitites, game_interface):
    player = Player(
        "Hiro",
        "Human",
        "Infiltrator",
        "The Player",
        21,
        17,
        100,
        12,
        15,
        20,
        15,
        11,
        '@',
        tcod.white,
        game_data,
        game_entities,
        game_interface
    )

    return player


# Initializes the game interface.
def init_interface(colors):
    game_interface = Interface()
    game_interface.wield_screen = game_interface.WieldScreen(0, 0)
    game_interface.description_screen = game_interface.DescriptionScreen( 0, 0)
    game_interface.inventory_screen = game_interface.InventoryScreen(0, 0)
    game_interface.stats_box = game_interface.StatsBox(
        MAP_WIDTH + 1, 0, SCREEN_WIDTH - MAP_WIDTH, SCREEN_HEIGHT)
    game_interface.message_box = game_interface.MessageBox(
        0, MAP_HEIGHT, MAP_WIDTH + 1, SCREEN_HEIGHT - MAP_HEIGHT)

    game_interface.message_box.add_msg(
        "Welcome to the High-Rise, punk!", colors["SYS_MSG"]
    )
    game_interface.message_box.add_msg(
        "Will you be the low-life who steals the secrets of the Mega Corp?", colors["SYS_MSG"]
    )

    return game_interface


# Spawns some enemies
# This is temporary, will eventually be done procedurally.
def spawn_enemies(game_data, game_entities, game_interface):
    enemy = Actor(
        "Rent-a-Cop",
        "Human",
        "Brawler",
        "A poor man paid nearly nothing to patrol the lower levels of the High-Rise.",
        23,
        18,
        100,
        12,
        15,
        20,
        15,
        11,
        ai.smart_melee,
        False,
        'C',
        tcod.yellow,
        game_data,
        game_entities,
        game_interface
    )
    enemy.add_inventory(Weapon(
        game_data.weapons["BATON"]["Name"],
        game_data.weapons["BATON"]["Description"],
        game_data.weapons["BATON"]["Damage"],
        game_data.weapons["BATON"]["Speed"],
        game_data.weapons["BATON"]["Accuracy"]
    ))
    enemy.attempt_wield(enemy.inventory[0]["Item"])


# Spawns some items
# This is temporary, will eventually be done procedurally.
def spawn_items(weapons, game_entities):
    ItemEntity(
        19,
        20,
        '(',  # Graphic hard-coded for now
        tcod.red,
        Weapon(
            weapons["SAMURAI_SWORD"]["Name"],
            weapons["SAMURAI_SWORD"]["Description"],
            weapons["SAMURAI_SWORD"]["Damage"],
            weapons["SAMURAI_SWORD"]["Speed"],
            weapons["SAMURAI_SWORD"]["Accuracy"]
        ),
        game_entities
    )


# Game Constants
SCREEN_WIDTH = 100
SCREEN_HEIGHT = 50
MAP_WIDTH = 70
MAP_HEIGHT = 42


# Game variables


GAME_DATA = Databases()
GAME_DATA.load_from_files()
window, root_console = init_tcod()

game_entities = GameEntities()

# Generate map (for now read from file, will be randomly generated)
# Initialize first so that it is drawn on bottom
map = Map(GAME_DATA)
map.read_map("Maps/game_map.txt", game_entities)

game_interface = init_interface(GAME_DATA.colors)

# THESE ARE TEMPORARY, JUST HERE FOR SOMETHING TO TEST
spawn_items(GAME_DATA.weapons, game_entities)
spawn_enemies(GAME_DATA, game_entities, game_interface)

# Init player last so they are rendered last.
player = init_player(GAME_DATA, game_entities, game_interface)
game_interface.stats_box.set_actor(player)

game_fsm = GameFSM(game_entities, game_interface, player)

# The game loop!
while True:
    game_fsm.handle_rendering(window, root_console)
    game_fsm.handle_input()
    game_fsm.handle_updates()
