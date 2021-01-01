import tcod
import entities
import interface
import map
import databases
import gamefsm
import ai
import items


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
def init_player(
        game_data: databases.Databases,
        entities__: entities.GameEntities,
        game_interface_: interface.Interface
) -> entities.Player:
    player_: entities.Player = entities.Player(
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
        entities__,
        game_interface_
    )

    return player_


# Initializes the game interface.Interface.
def init_interface(colors: dict) -> interface.Interface:
    game_interface_: interface.Interface = interface.Interface(SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
    game_interface_.message_box.add_msg(
        "Welcome to the High-Rise, punk!", colors["SYS_MSG"]
    )
    game_interface_.message_box.add_msg(
        "Will you be the low-life who steals the secrets of the Mega Corp?", colors["SYS_MSG"]
    )

    return game_interface_


# The following functions are temporary, will eventually be done procedurally.
def spawn_enemies(
        game_data_: databases.Databases,
        entities__: entities.GameEntities,
        game_interface_: interface.Interface
) -> None:
    enemy: entities.Actor = entities.Actor(
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
        entities__,
        game_interface_
    )
    enemy.add_inventory(items.Weapon(
        game_data_.weapons["BATON"]["Name"],
        game_data_.weapons["BATON"]["Description"],
        game_data_.weapons["BATON"]["Damage"],
        game_data_.weapons["BATON"]["Speed"],
        game_data_.weapons["BATON"]["Accuracy"]
    ))
    enemy.attempt_wield(enemy.inventory[0]["Item"])


def spawn_items(weapons: dict, entities__: entities.GameEntities) -> None:
    entities.ItemEntity(
        19,
        20,
        weapons["SAMURAI_SWORD"]["Name"],
        weapons["SAMURAI_SWORD"]["Description"],
        ')',  # Graphic hard-coded for now
        tcod.red,
        items.Weapon(
            weapons["SAMURAI_SWORD"]["Name"],
            weapons["SAMURAI_SWORD"]["Description"],
            weapons["SAMURAI_SWORD"]["Damage"],
            weapons["SAMURAI_SWORD"]["Speed"],
            weapons["SAMURAI_SWORD"]["Accuracy"]
        ),
        entities__
    )

    entities.ItemEntity(
        18,
        20,
        weapons["TEC9"]["Name"],
        weapons["TEC9"]["Description"],
        ')',  # Graphic hard-coded for now
        tcod.red,
        items.Weapon(
            weapons["TEC9"]["Name"],
            weapons["TEC9"]["Description"],
            weapons["TEC9"]["Damage"],
            weapons["TEC9"]["Speed"],
            weapons["TEC9"]["Accuracy"]
        ),
        entities__
    )


def spawn_terminals(
        game_data_: databases.Databases,
        entities__: entities.GameEntities,
        game_interface_: interface.Interface
) -> None:
    entities.Terminal(60, 19, game_data_, entities__, game_interface_)


def spawn_cameras(game_data_: databases.Databases, entities__: entities.GameEntities) -> None:
    entities.Camera(58, 16, game_data_, entities__)


# Game Constants
SCREEN_WIDTH: int = 100
SCREEN_HEIGHT: int = 50
MAP_WIDTH: int = 70
MAP_HEIGHT: int = 42


GAME_DATA: databases.Databases = databases.Databases()
GAME_DATA.load_from_files()
window: tcod.context.Context
root_console: tcod.Console
(window, root_console) = init_tcod()

entities_: entities.GameEntities = entities.GameEntities()

# Generate map (for now read from file, will be randomly generated)
# Initialize first so that it is drawn on bottom
game_map: map.Map = map.Map(GAME_DATA)
game_map.read_map("Maps/game_map.txt", entities_)

game_interface: interface.Interface = init_interface(GAME_DATA.colors)

# THESE ARE TEMPORARY, JUST HERE FOR SOMETHING TO TEST
spawn_items(GAME_DATA.weapons, entities_)
spawn_enemies(GAME_DATA, entities_, game_interface)
spawn_terminals(GAME_DATA, entities_, game_interface)
spawn_cameras(GAME_DATA, entities_)

# Init player last so they are rendered last.
player: entities.Player = init_player(GAME_DATA, entities_, game_interface)
game_interface.stats_box.set_actor(player)

game_fsm: gamefsm.GameFSM = gamefsm.GameFSM(entities_, game_interface, player, (MAP_WIDTH, MAP_HEIGHT))

# The game loop!
while True:
    game_fsm.handle_rendering(window, root_console)
    game_fsm.handle_input()
    game_fsm.handle_updates()
