from enum import Enum, auto


def set_state(state):
    global game_state
    global prev_game_state

    prev_game_state = game_state
    game_state = state


class GameStates(Enum):
    PLAYING = auto(),
    INVENTORY = auto()


class Actions(Enum):
    MOVE = auto(),
    ATK_MELEE = auto(),
    WIELD = auto(),
    OPEN_DOOR = auto(),
    CLOSE_DOOR = auto(),
    REST = auto(),
    PICKUP = auto()


# How many turns a rest action takes.
REST_TIME = 10

# How much an inventory can hold.
MAX_INVENTORY_SIZE = 52

# The current state of the game.
game_state = GameStates.PLAYING

# Stores the previous game state to jump to it quickly.
prev_game_state = None

# The substate of the game (ie: playing but waiting to select ranged target)
game_substate = None

# The amount of time that has passed in the game
time = 0

# A list of all entities on the current floor
entities = []

# A list of all actors on the current floor
actors = []

# A list of all doors on the current floor
doors = []

# A list of all items on the current floor
items = []

# The heads-up display
HUD = None

# The panel on the screen showing in-game messages
msg_box = None

# A database of NPCs
npcs = None

# A database of weapons
weapons = None

# A database of tiles
tiles = None

# A database of colors
colors = None
