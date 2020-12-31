import tcod
import ai
from interface import Interface
from map import Map
from actor import Actor
from player import Player
from item_entity import ItemEntity
from terminal import Terminal
from camera import Camera
from weapon import Weapon
from databases import Databases
from gamefsm import GameFSM
from game_entities import GameEntities


# Initializes tcod and returns a window and console.
def init_tcod() -> tuple[tcod.context.Context, tcod.Console]:
    # Initialize tcod and game console
    tileset: tcod.tileset.Tileset = tcod.tileset.load_tilesheet(
        "Tilesets/tileset.png",
        32,
        8,
        tcod.tileset.CHARMAP_TCOD
    )

    window_: tcod.context.Context = tcod.context.new_terminal(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        tileset=tileset,
        title="High-Rise: Low-Lives",
        vsync=True
    )
    console: tcod.Console = tcod.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order='F')

    return window_, console


# Initializes the player
def init_player(game_data: Databases, game_entities_: GameEntities, game_interface_: Interface) -> Player:
    player_: Player = Player(
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
        game_entities_,
        game_interface_
    )

    return player_


# Initializes the game interface.
def init_interface(colors: dict) -> Interface:
    game_interface_: Interface = Interface(SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
    game_interface_.message_box.add_msg(
        "Welcome to the High-Rise, punk!", colors["SYS_MSG"]
    )
    game_interface_.message_box.add_msg(
        "Will you be the low-life who steals the secrets of the Mega Corp?", colors["SYS_MSG"]
    )

    return game_interface_


# The following functions are temporary, will eventually be done procedurally.
def spawn_enemies(game_data_: Databases, game_entities_: GameEntities, game_interface_: Interface) -> None:
    enemy: Actor = Actor(
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
        game_data_,
        game_entities_,
        game_interface_
    )
    enemy.add_inventory(Weapon(
        game_data_.weapons["BATON"]["Name"],
        game_data_.weapons["BATON"]["Description"],
        game_data_.weapons["BATON"]["Damage"],
        game_data_.weapons["BATON"]["Speed"],
        game_data_.weapons["BATON"]["Accuracy"]
    ))
    enemy.attempt_wield(enemy.inventory[0]["Item"])


def spawn_items(weapons: dict, game_entities_: GameEntities) -> None:
    ItemEntity(
        19,
        20,
        weapons["SAMURAI_SWORD"]["Name"],
        weapons["SAMURAI_SWORD"]["Description"],
        ')',  # Graphic hard-coded for now
        tcod.red,
        Weapon(
            weapons["SAMURAI_SWORD"]["Name"],
            weapons["SAMURAI_SWORD"]["Description"],
            weapons["SAMURAI_SWORD"]["Damage"],
            weapons["SAMURAI_SWORD"]["Speed"],
            weapons["SAMURAI_SWORD"]["Accuracy"]
        ),
        game_entities_
    )

    ItemEntity(
        18,
        20,
        weapons["TEC9"]["Name"],
        weapons["TEC9"]["Description"],
        ')',  # Graphic hard-coded for now
        tcod.red,
        Weapon(
            weapons["TEC9"]["Name"],
            weapons["TEC9"]["Description"],
            weapons["TEC9"]["Damage"],
            weapons["TEC9"]["Speed"],
            weapons["TEC9"]["Accuracy"]
        ),
        game_entities_
    )


def spawn_terminals(game_data_: Databases, game_entities_: GameEntities, game_interface_: Interface) -> None:
    Terminal(60, 19, game_data_, game_entities_, game_interface_)


def spawn_cameras(game_data_: Databases, game_entities_: GameEntities) -> None:
    Camera(58, 16, game_data_, game_entities_)


# Game Constants
SCREEN_WIDTH: int = 100
SCREEN_HEIGHT: int = 50
MAP_WIDTH: int = 70
MAP_HEIGHT: int = 42


GAME_DATA: Databases = Databases()
GAME_DATA.load_from_files()
window: tcod.context.Context
root_console: tcod.Console
(window, root_console) = init_tcod()

game_entities: GameEntities = GameEntities()

# Generate map (for now read from file, will be randomly generated)
# Initialize first so that it is drawn on bottom
game_map: Map = Map(GAME_DATA)
game_map.read_map("Maps/game_map.txt", game_entities)

game_interface: Interface = init_interface(GAME_DATA.colors)

# THESE ARE TEMPORARY, JUST HERE FOR SOMETHING TO TEST
spawn_items(GAME_DATA.weapons, game_entities)
spawn_enemies(GAME_DATA, game_entities, game_interface)
spawn_terminals(GAME_DATA, game_entities, game_interface)
spawn_cameras(GAME_DATA, game_entities)

# Init player last so they are rendered last.
player: Player = init_player(GAME_DATA, game_entities, game_interface)
game_interface.stats_box.set_actor(player)

game_fsm: GameFSM = GameFSM(game_entities, game_interface, player, (MAP_WIDTH, MAP_HEIGHT))

# The game loop!
while True:
    game_fsm.handle_rendering(window, root_console)
    game_fsm.handle_input()
    game_fsm.handle_updates()
