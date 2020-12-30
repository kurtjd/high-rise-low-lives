import entity


# Represents static map tiles like floors and walls.
class Tile(entity.Entity):
    def __init__(self, x, y, name, desc, blocked, graphic, color, game_entities):
        super().__init__(x, y, name, desc, blocked, graphic, color, game_entities)
        game_entities.tiles.append(self)
