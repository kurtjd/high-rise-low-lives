import entity
import game_entities


# Represents static map tiles like floors and walls.
class Tile(entity.Entity):
    def __init__(
            self,
            x: int,
            y: int,
            name: str,
            desc: str,
            blocked: bool,
            graphic: str,
            color: tuple[int, int, int],
            game_entities_: "game_entities.GameEntities"
    ) -> None:
        super().__init__(x, y, name, desc, blocked, graphic, color, game_entities_)
        game_entities_.tiles.append(self)
