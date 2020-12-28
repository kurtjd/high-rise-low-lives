from enum import Enum, auto


def set_state(state):
    global game_state
    global prev_game_states

    prev_game_states.append(game_state)
    game_state = state


# Reverts to a previous state.
def reverse_state():
    global game_state
    global prev_game_states

    game_state = prev_game_states.pop()


class GameStates(Enum):
    PLAYING = auto(),
    EXAMINING = auto(),
    INVENTORY = auto(),
    SELECT_WIELD = auto(),
    READ_DESC = auto()


# The current state of the game.
game_state = GameStates.PLAYING

# Stores the previous game state to jump to it quickly.
prev_game_states = []

# The substate of the game (ie: playing but waiting to select ranged target)
game_substate = None


# How many turns a rest action takes.
REST_TIME = 10

# How much an inventory can hold.
MAX_INVENTORY_SIZE = 52

# The amount of time that has passed in the game
time = 0

# The current floor the player is on.
floor_on = 1

# What the player is currently reading.
player_reading = None

# Location of what the player is examining
examine_location = [0, 0]
