from typing import Optional
import tcod
import game_entities


class Entity:
    # ~~~ STATIC METHODS ~~~

    def __init__(
            self,
            x: int,
            y: int,
            name: str,
            desc: str,
            blocked: bool,
            graphic: str,
            color: Optional[tuple[int, int, int]],
            game_entities_: "game_entities.GameEntities"
    ) -> None:
        self.x: int = x
        self.y: int = y
        self.name: str = name
        self.desc: str = desc
        self.graphic: str = graphic
        self.color: Optional[tuple[int, int, int]] = color
        self.bgcolor: Optional[tuple[int, int, int]] = None
        self.blocked: bool = blocked
        self.game_entities: game_entities.GameEntities = game_entities_
        game_entities_.all.append(self)

    # ~~~ PUBLIC METHODS ~~~

    # Draws a game entity to the screen
    def render(self, console: tcod.Console) -> None:
        console.print(x=self.x, y=self.y, string=self.graphic, fg=self.color, bg=self.bgcolor)

    def update(self, game_time: int) -> None:
        pass

    def remove(self) -> None:
        for entity in enumerate(self.game_entities.all):
            if entity[1] is self:
                self.game_entities.all.pop(entity[0])
