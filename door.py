import entity
import globals


# ~~~ STATIC METHODS ~~~

# Returns the Door at a given position
# There can only ever be one Door at a position so return the first one we find
def get_door_at(x, y):
    for door_at_pos in globals.doors:
        if door_at_pos.x == x and door_at_pos.y == y:
            return door_at_pos
    return None


class Door(entity.Entity):
    # ~~~ PRIVATE METHODS ~~~

    def __init__(self, x, y, graphic, color, blocked=True):
        super().__init__(x, y, graphic, color, blocked)
        self.opened = False
        self.locked = False
        globals.doors.append(self)

    # ~~~ PUBLIC METHODS ~~~

    # Changes the appearance of the door and makes it no longer blocked.
    def open(self):
        self.opened = True
        self.blocked = False
        self.graphic = globals.tiles["DOOR_OPEN"]["Character"]
        self.color = globals.tiles["DOOR_OPEN"]["Color"]

    def close(self):
        self.opened = False
        self.blocked = True
        self.graphic = globals.tiles["DOOR_CLOSED"]["Character"]
        self.color = globals.tiles["DOOR_CLOSED"]["Color"]
