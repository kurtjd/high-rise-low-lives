import globals


# ~~~ STATIC METHODS ~~~

def update_all():
    for entity in globals.entities:
        entity.update()


# Draws all game entities to the screen.
def render_all(console):
    for entity in globals.entities:
        entity.render(console)


# Returns a list of entities at a given position
def get_entities_at(x, y):
    entities_at_pos = []

    for entity in globals.entities:
        if entity.x == x and entity.y == y:
            entities_at_pos.append(entity)

    return entities_at_pos


class Entity:
    # ~~~ STATIC METHODS ~~~

    def __init__(self, x, y, graphic, color, blocked=False):
        self.x = x
        self.y = y
        self.graphic = graphic
        self.color = color
        self.blocked = blocked
        globals.entities.append(self)  # Adds self to list of global game entities

    # ~~~ PUBLIC METHODS ~~~

    # Draws a game entity to the screen
    def render(self, console):
        console.print(x=self.x, y=self.y, string=self.graphic, fg=self.color)

    def update(self):
        pass

    def remove(self):
        for entity in enumerate(globals.entities):
            if entity[1] is self:
                globals.entities.pop(entity[0])
