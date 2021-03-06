import tcod
import interface
import map
import databases
import game_engine
import ai
import items
import game_entities.entities
import game_entities.actor
import game_entities.turret
import game_entities.item_entity
import game_entities.terminal
import game_entities.camera
import game_entities.trap


# The following functions are temporary, will eventually be done procedurally.
def spawn_enemies(
        game_data_: databases.Databases,
        entities__: game_entities.entities.GameEntities,
        game_interface_: interface.Interface
) -> None:
    enemy1: game_entities.actor.Actor = game_entities.actor.Actor(
        "Rent-a-Cop",
        "Human",
        "Brawler",
        "A poor man paid nearly nothing to patrol the lower levels of the High-Rise.",
        35,
        15,
        100,
        12,
        15,
        20,
        15,
        11,
        ai.smart_melee,
        'C',
        tcod.blue,
        game_data_,
        entities__,
        game_interface_
    )
    enemy1.add_inventory(items.Weapon(
        game_data_.weapons["BATON"]["Name"],
        game_data_.weapons["BATON"]["Description"],
        game_data_.weapons["BATON"]["Damage"],
        game_data_.weapons["BATON"]["Speed"],
        game_data_.weapons["BATON"]["Accuracy"],
        game_data_.weapons["BATON"]["Distance"],
        game_data_.weapons["BATON"]["Type"],
        game_data_.weapons["BATON"]["Hands"]
    ))
    enemy1.attempt_wield(enemy1.inventory['a']["Item"])

    enemy2: game_entities.actor.Actor = game_entities.actor.Actor(
        "Mercenary",
        "Human",
        "Gunslinger",
        "Hobbies include long walks on the beach and killing for money.",
        36,
        22,
        100,
        12,
        15,
        20,
        15,
        11,
        ai.smart_ranged,
        'M',
        tcod.yellow,
        game_data_,
        entities__,
        game_interface_
    )
    enemy2.add_inventory(items.Weapon(
        game_data_.weapons["TEC9"]["Name"],
        game_data_.weapons["TEC9"]["Description"],
        game_data_.weapons["TEC9"]["Damage"],
        game_data_.weapons["TEC9"]["Speed"],
        game_data_.weapons["TEC9"]["Accuracy"],
        game_data_.weapons["TEC9"]["Distance"],
        game_data_.weapons["TEC9"]["Type"],
        game_data_.weapons["TEC9"]["Hands"],
        game_data_.weapons["TEC9"]["Caliber"],
        game_data_.weapons["TEC9"]["Mag Capacity"]
    ))
    enemy2.attempt_wield(enemy2.inventory['a']["Item"])

    game_entities.turret.Turret(46, 6, game_data_, entities__, game_interface_)


def spawn_items(
        game_data_: databases.Databases,
        entities__: game_entities.entities.GameEntities,
        game_interface_: interface.Interface
) -> None:
    weapons: dict = game_data_.weapons
    throwables: dict = game_data_.throwables
    drugs: dict = game_data_.drugs
    power_sources: dict = game_data_.power_sources
    misc_items: dict = game_data_.misc_items
    ammo: dict = game_data_.ammo

    game_entities.item_entity.ItemEntity(
        22,
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
            weapons["SAMURAI_SWORD"]["Accuracy"],
            weapons["SAMURAI_SWORD"]["Distance"],
            weapons["SAMURAI_SWORD"]["Type"],
            weapons["SAMURAI_SWORD"]["Hands"],
        ),
        game_data_,
        entities__,
        game_interface_
    )

    game_entities.item_entity.ItemEntity(
        23,
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
            weapons["TEC9"]["Accuracy"],
            weapons["TEC9"]["Distance"],
            weapons["TEC9"]["Type"],
            weapons["TEC9"]["Hands"],
            weapons["TEC9"]["Caliber"],
            weapons["TEC9"]["Mag Capacity"]
        ),
        game_data_,
        entities__,
        game_interface_
    )

    game_entities.item_entity.ItemEntity(
        23,
        18,
        throwables["GRENADE"]["Name"],
        throwables["GRENADE"]["Description"],
        '(',  # Graphic hard-coded for now
        tcod.amber,
        items.Grenade(
            throwables["GRENADE"]["Name"],
            throwables["GRENADE"]["Description"],
            throwables["GRENADE"]["Damage"],
            throwables["GRENADE"]["Blast Radius"],
            throwables["GRENADE"]["Fuse"]
        ),
        game_data_,
        entities__,
        game_interface_
    )

    game_entities.item_entity.ItemEntity(
        21,
        18,
        drugs["STITCH"]["Name"],
        drugs["STITCH"]["Description"],
        '!',  # Graphic hard-coded for now
        tcod.purple,
        items.Drug(
            drugs["STITCH"]["Name"],
            drugs["STITCH"]["Description"],
            drugs["STITCH"]["Effect"]
        ),
        game_data_,
        entities__,
        game_interface_
    )

    game_entities.item_entity.ItemEntity(
        20,
        18,
        power_sources["BATTERY"]["Name"],
        power_sources["BATTERY"]["Description"],
        ':',  # Graphic hard-coded for now
        tcod.orange,
        items.PowerSource(
            power_sources["BATTERY"]["Name"],
            power_sources["BATTERY"]["Description"],
            power_sources["BATTERY"]["Charge Held"],
            power_sources["BATTERY"]["Discharge Time"],
        ),
        game_data_,
        entities__,
        game_interface_
    )

    game_entities.item_entity.ItemEntity(
        20,
        19,
        misc_items["CIGARETTE"]["Name"],
        misc_items["CIGARETTE"]["Description"],
        misc_items["CIGARETTE"]["Graphic"],
        misc_items["CIGARETTE"]["Color"],
        items.Cigarette(misc_items["CIGARETTE"]["Name"], misc_items["CIGARETTE"]["Description"]),
        game_data_,
        entities__,
        game_interface_
    )

    game_entities.item_entity.ItemEntity(
        18,
        17,
        ammo["9MM_FMJ"]["Name"],
        ammo["9MM_FMJ"]["Description"],
        '(',  # Graphic hard-coded for now
        tcod.gray,
        items.Ammo(
            ammo["9MM_FMJ"]["Name"],
            ammo["9MM_FMJ"]["Description"],
            ammo["9MM_FMJ"]["Caliber"],
            ammo["9MM_FMJ"]["Type"]
        ),
        game_data_,
        entities__,
        game_interface_
    )


def spawn_terminals(
        game_data_: databases.Databases,
        entities__: game_entities.entities.GameEntities,
        game_interface_: interface.Interface
) -> None:
    game_entities.terminal.Terminal(60, 19, game_data_, entities__, game_interface_)


def spawn_cameras(
        game_data_: databases.Databases,
        entities__: game_entities.entities.GameEntities,
        game_interface_: interface.Interface
) -> None:
    game_entities.camera.Camera(58, 16, game_data_, entities__, game_interface_)
    game_entities.camera.Camera(30, 11, game_data_, entities__, game_interface_)


def spawn_traps(
        game_data_: databases.Databases,
        entities__: game_entities.entities.GameEntities,
        game_interface_: interface.Interface
) -> None:
    game_entities.trap.Trap(60, 18, game_data_, entities__, game_interface_)
    game_entities.trap.Trap(33, 14, game_data_, entities__, game_interface_)
# END TEMPORARY STUFF


def init_tcod() -> tuple[tcod.context.Context, tcod.Console]:
    """ Initializes tcod and returns a window and console. """

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


def init_player(
        game_data: databases.Databases,
        entities__: game_entities.entities.GameEntities,
        game_interface_: interface.Interface
) -> game_entities.actor.Player:
    """Initializes the player entity."""

    player_: game_entities.actor.Player = game_entities.actor.Player(
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


def init_interface(game_db: databases.Databases) -> interface.Interface:
    """Initializes the game interface."""

    game_interface_: interface.Interface = interface.Interface(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        MAP_WIDTH,
        MAP_HEIGHT
    )
    game_interface_.message_box.add_msg(
        "Welcome to the High-Rise, punk!", game_db.colors["SYS_MSG"]
    )
    game_interface_.message_box.add_msg(
        "Will you be the low-life who steals the secrets of the Mega Corp?", game_db.colors["SYS_MSG"]
    )

    return game_interface_


# Define screen and map size.
SCREEN_WIDTH: int = 100
SCREEN_HEIGHT: int = 50
MAP_WIDTH: int = 70
MAP_HEIGHT: int = 42


# Initialize game objects and assign.
GAME_DATA: databases.Databases = databases.Databases()
GAME_DATA.load_from_files()
window: tcod.context.Context
root_console: tcod.Console
(window, root_console) = init_tcod()
entities_: game_entities.entities.GameEntities = game_entities.entities.GameEntities(window, root_console)
game_interface: interface.Interface = init_interface(GAME_DATA)

# Generate map (for now read from file, will be randomly generated)
# Initialize first so that it is drawn on bottom
game_map: map.Map = map.Map(GAME_DATA, entities_, game_interface)
game_map.read_map("Maps/game_map.txt")

# THESE ARE TEMPORARY, JUST HERE FOR SOMETHING TO TEST
spawn_items(GAME_DATA, entities_, game_interface)
spawn_enemies(GAME_DATA, entities_, game_interface)
spawn_terminals(GAME_DATA, entities_, game_interface)
spawn_cameras(GAME_DATA, entities_, game_interface)
spawn_traps(GAME_DATA, entities_, game_interface)
entities_.doors[1].locked = True  # Just lock an arbitrary door as a test.
# END TEMPORARY STUFF

# Init player last so they are rendered last.
player: game_entities.actor.Player = init_player(GAME_DATA, entities_, game_interface)
game_interface.stats_box.set_actor(player)

# Initialize game engine.
engine: game_engine.GameEngine = game_engine.GameEngine(entities_, game_interface,
                                                        GAME_DATA, player, (MAP_WIDTH, MAP_HEIGHT))

# The game loop!
while True:
    engine.handle_rendering(window, root_console)
    engine.handle_input()
    engine.handle_updates()
