from typing import Any
import actor
import game_entities
import databases
import interface


# This is a small class since the player mostly shares characteristics with other actors except a few things.

class Player(actor.Actor):
    def __init__(
            self,
            name: str,
            race: str,
            class_name: str,
            desc: str,
            x: int,
            y: int,
            health: int,
            muscle: int,
            smarts: int,
            reflexes: int,
            wits: int,
            grit: int,
            graphic: str,
            color: tuple[int, int, int],
            game_data: databases.Databases,
            game_entities_: "game_entities.GameEntities",
            game_interface: interface.Interface
    ) -> None:
        super().__init__(name, race, class_name, desc, x, y, health, muscle, smarts, reflexes, wits, grit,
                         None, True, graphic, color, game_data, game_entities_, game_interface)
        self.examine_target: Any = None
