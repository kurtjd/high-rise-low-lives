import json
import tcod
import globals
import interface
import map
import entity
import actor
import item_entity
import item
import weapon
import ai


# Game Constants
SCREEN_WIDTH = 100
SCREEN_HEIGHT = 50
MAP_WIDTH = 70
MAP_HEIGHT = 42


# Loads json files and makes the data availble for the game.
def load_data():
    # Colors
    with open("Data/colors.dat") as data_file:
        globals.colors = json.load(data_file)

    # Tiles
    with open("Data/tiles.dat") as data_file:
        globals.tiles = json.load(data_file)
    # Convert ASCII code of each tile to character.
    for tile in globals.tiles:
        globals.tiles[tile]["Character"] = chr(globals.tiles[tile]["Character"])

    # NPCs
    with open("Data/npcs.dat") as data_file:
        globals.npcs = json.load(data_file)

    # Weapons
    with open("Data/weapons.dat") as data_file:
        globals.weapons = json.load(data_file)


# Handles all rendering
def handle_rendering(console):
    if globals.game_state == globals.GameStates.PLAYING:
        globals.HUD.render(root_console)
        globals.msg_box.render(root_console)
        entity.render_all(root_console)

    elif globals.game_state == globals.GameStates.INVENTORY:
        interface.render_inventory_screen(player.inventory, console)

    # Rendering that happens regardless of state.
    window.present(console)
    console.clear()


# Handles all input
def handle_input():
    # Input that happens regardless of state.
    for event in tcod.event.wait():
        if event.type == "QUIT":
            raise SystemExit()
        elif event.type == "KEYDOWN":
            key = event.sym

            if key == tcod.event.K_ESCAPE:
                if globals.game_state == globals.GameStates.PLAYING:
                    raise SystemExit()
                else:
                    globals.set_state(globals.prev_game_state)

            if globals.game_state == globals.GameStates.PLAYING:
                if key == tcod.event.K_UP:
                    player.attempt_move(0, -1)
                elif key == tcod.event.K_DOWN:
                    player.attempt_move(0, 1)
                elif key == tcod.event.K_LEFT:
                    player.attempt_move(-1, 0)
                elif key == tcod.event.K_RIGHT:
                    player.attempt_move(1, 0)
                elif key == tcod.event.K_PERIOD:
                    player.attempt_rest()
                elif key == tcod.event.K_SEMICOLON:
                    player.attempt_pickup()
                elif (event.mod & tcod.event.KMOD_CTRL) and key == tcod.event.K_c:
                    player.attempt_close_door()
                # This is temporary. Will later ask what to wield.
                elif key == tcod.event.K_w:
                    player.attempt_wield(player.inventory[0]["Item"])
                elif key == tcod.event.K_i:
                    globals.set_state(globals.GameStates.INVENTORY)

            elif globals.game_state == globals.GameStates.INVENTORY:
                if key == tcod.event.K_i:
                    globals.set_state(globals.GameStates.PLAYING)


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
def init_player():
    player = actor.Actor(
        21,
        17,
        '@',
        tcod.white,
        "Hiro",
        "Human",
        "Infiltrator",
        "The Player",
        100,
        12,
        15,
        20,
        15,
        11,
        None,
        True
    )

    # Give the player a samurai sword for now.
    player.add_inventory(weapon.Weapon(
        globals.weapons["SAMURAI_SWORD"]["Name"],
        globals.weapons["SAMURAI_SWORD"]["Description"],
        globals.weapons["SAMURAI_SWORD"]["Damage"],
        globals.weapons["SAMURAI_SWORD"]["Speed"],
        globals.weapons["SAMURAI_SWORD"]["Accuracy"]
    ))

    return player


# Initializes the game interface.
def init_interface():
    globals.HUD = interface.HUD(MAP_WIDTH + 1, 0, SCREEN_WIDTH - MAP_WIDTH, SCREEN_HEIGHT)
    globals.msg_box = interface.Messages(0, MAP_HEIGHT, MAP_WIDTH + 1, SCREEN_HEIGHT - MAP_HEIGHT)

    interface.send_msg(
        globals.msg_box,
        "Welcome to the High-Rise, punk!", globals.colors["SYS_MSG"]
    )
    interface.send_msg(
        globals.msg_box,
        "Will you be the low-life who steals the secrets of the Mega Corp?", globals.colors["SYS_MSG"]
    )


# Spawns some enemies
# This is temporary, will eventually be done procedurally.
def spawn_enemies():
    actor.Actor(
        23,
        18,
        'M',
        tcod.yellow,
        "Mercenary",
        "Human",
        "Gunslinger",
        "A mercenary hired to patrol the high-rise.",
        100,
        25,
        8,
        18,
        12,
        20,
        ai.smart_melee,
        False
    )


# Spawns some items
# This is temporary, will eventually be done procedurally.
def spawn_items():
    item_entity.ItemEntity(
        19,
        20,
        ']',  # Graphic hard-coded for now
        tcod.white,
        weapon.Weapon(
            globals.weapons["BATON"]["Name"],
            globals.weapons["BATON"]["Description"],
            globals.weapons["BATON"]["Damage"],
            globals.weapons["BATON"]["Speed"],
            globals.weapons["BATON"]["Accuracy"]
        )
    )


# Handles all updating
def handle_updates():
    if globals.game_state == globals.GameStates.PLAYING:
        globals.HUD.update(player.health, player.wielding, globals.time)

        # Updates the game every tick of time in between player actions
        while player.action_delay >= 0:
            globals.time += 1
            entity.update_all()


window, root_console = init_tcod()
load_data()

# Generate map (for now read from file, will be randomly generated)
# Initialize first so that it is drawn on bottom
map = map.read_map("Maps/game_map.txt")

init_interface()
spawn_items()
spawn_enemies()
player = init_player()

# The game loop!
while True:
    handle_rendering(root_console)
    handle_input()
    handle_updates()
