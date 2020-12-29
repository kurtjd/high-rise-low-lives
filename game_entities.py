class GameEntities:
    def __init__(self):
        self.all = []
        self.actors = []
        self.doors = []
        self.items = []

    # Returns a list of entities at a given position
    def get_all_at(self, x, y):
        entities_at_pos = []

        for entity in self.all:
            if entity.x == x and entity.y == y:
                entities_at_pos.append(entity)

        return entities_at_pos

    # Returns the Actor at a given position
    # There can only ever be one Actor at a position so return the first one we find
    def get_actor_at(self, x, y):
        for actor_at_pos in self.actors:
            if actor_at_pos.x == x and actor_at_pos.y == y:
                return actor_at_pos
        return None

    # Returns the Door at a given position
    # There can only ever be one Door at a position so return the first one we find
    def get_door_at(self, x, y):
        for door_at_pos in self.doors:
            if door_at_pos.x == x and door_at_pos.y == y:
                return door_at_pos
        return None

    # Returns the Item entities at a given position
    def get_items_at(self, x, y):
        items_at_pos = []

        for item_at_pos in self.items:
            if item_at_pos.x == x and item_at_pos.y == y:
                items_at_pos.append(item_at_pos)

        return items_at_pos

    # Draws all game entities to the screen.
    def render_all(self, console):
        for entity in self.all:
            entity.render(console)

    # Called every tick of time to update entities.
    def update_all(self, game_time):
        for entity in self.all:
            entity.update(game_time)

    # Clears and resets all the lists.
    def reset(self):
        self.all = []
        self.actors = []
        self.doors = []
        self.items = []
