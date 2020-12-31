from typing import Optional
import tcod
import entity
import tile
import actor
import door
import item_entity
import terminal
import camera


class GameEntities:
    def __init__(self) -> None:
        self.all: list[entity.Entity] = []
        self.tiles: list[tile.Tile] = []
        self.actors:  list[actor.Actor] = []
        self.doors:  list[door.Door] = []
        self.items:  list[item_entity.ItemEntity] = []
        self.terminals:  list[terminal.Terminal] = []
        self.cameras:  list[camera.Camera] = []

    # Returns a list of entities at a given position
    def get_all_at(self, x: int, y: int) -> list[entity.Entity]:
        return [entity_ for entity_ in self.all if entity_.x == x and entity_.y == y]

    # Returns the Actor at a given position
    # There can only ever be one Actor at a position so return the first one we find
    def get_actor_at(self, x: int, y: int) -> Optional["actor.Actor"]:
        for actor_ in self.actors:
            if actor_.x == x and actor_.y == y:
                return actor_
        return None

    # Returns the Door at a given position
    # There can only ever be one Door at a position so return the first one we find
    def get_door_at(self, x: int, y: int) -> Optional[door.Door]:
        for door_ in self.doors:
            if door_.x == x and door_.y == y:
                return door_
        return None

    # Returns the Item entities at a given position
    def get_items_at(self, x: int, y: int) -> list[item_entity.ItemEntity]:
        return [item_ for item_ in self.items if item_.x == x and item_.y == y]

    # Returns the Terminal at a given position
    # There can only ever be one Actor at a position so return the first one we find
    def get_terminal_at(self, x: int, y: int) -> Optional[terminal.Terminal]:
        for terminal_ in self.terminals:
            if terminal_.x == x and terminal_.y == y:
                return terminal_
        return None

    # Draws all game entities to the screen.
    def render_all(self, console: tcod.Console) -> None:
        for entity_ in self.all:
            entity_.render(console)

    # Called every tick of time to update entities.
    def update_all(self, game_time: int) -> None:
        for entity_ in self.all:
            entity_.update(game_time)

    # Clears and resets all the lists.
    def reset(self) -> None:
        self.all = []
        self.actors = []
        self.doors = []
        self.items = []
