from __future__ import annotations
from typing import Optional, Any
import game_entities.entity
import game_entities.actor
import game_entities.tile
import game_entities.item_entity
import game_entities.camera
import game_entities.terminal
import game_entities.door
import game_entities.turret
import game_entities.explosive
import game_entities.trap
import game_entities.vent


class EntityManager:
    """Stores and manages the lists of different game entities."""

    def __init__(self, window: Any, surface: Any) -> None:
        self.all: list[game_entities.entity.Entity] = []
        self.tiles: list[game_entities.tile.Tile] = []
        self.actors: list[game_entities.actor.Actor] = []
        self.turrets: list[game_entities.turret.Turret] = []
        self.doors: list[game_entities.door.Door] = []
        self.items: list[game_entities.item_entity.ItemEntity] = []
        self.terminals: list[game_entities.terminal.Terminal] = []
        self.cameras: list[game_entities.camera.Camera] = []
        self.traps: list[game_entities.trap.Trap] = []
        self.vents: list[game_entities.vent.Vent] = []
        self.explosives: list[game_entities.explosive.Explosive] = []
        self.player: Optional[game_entities.actor.Player] = None

        self.window: Any = window
        self.surface: Any = surface

    def get_all_at(self, x: int, y: int) -> list[game_entities.entity.Entity]:
        """Returns all the entities on a tile."""

        return [entity_ for entity_ in self.all if entity_.x == x and entity_.y == y]

    def get_top_entity_at(self, x: int, y: int, ignore_invis: bool = False) -> Optional[game_entities.entity.Entity]:
        """Returns the top-most entity on a tile."""

        if not ignore_invis:
            return self.get_all_at(x, y)[-1]
        else:
            # Get the top-most entity that is visible.
            all_: list[game_entities.entity.Entity] = self.get_all_at(x, y)
            all_.reverse()
            for entity_ in all_:
                if entity_.visible:
                    return entity_
            return all_[0]  # If no visible entities at position, return the top invisible one anyway.

    def get_actor_at(self, x: int, y: int) -> Optional[game_entities.actor.Actor]:
        """Returns the actor on a tile if there is one."""

        for actor_ in self.actors:
            if actor_.x == x and actor_.y == y:
                return actor_
        return None

    def get_door_at(self, x: int, y: int) -> Optional[game_entities.door.Door]:
        """Returns the door on a tile if there is one."""

        for door_ in self.doors:
            if door_.x == x and door_.y == y:
                return door_
        return None

    def get_items_at(self, x: int, y: int) -> list[game_entities.item_entity.ItemEntity]:
        """Returns all the item entities on a tile."""

        return [item_ for item_ in self.items if item_.x == x and item_.y == y]

    def get_terminal_at(self, x: int, y: int) -> Optional[game_entities.terminal.Terminal]:
        """Returns the terminal on a tile if there is one."""

        for terminal_ in self.terminals:
            if terminal_.x == x and terminal_.y == y:
                return terminal_
        return None

    def get_trap_at(self, x: int, y: int) -> Optional[game_entities.trap.Trap]:
        """Returns the trap on a tile if there is one."""

        for trap_ in self.traps:
            if trap_.x == x and trap_.y == y:
                return trap_
        return None

    def get_vent_at(self, x: int, y: int) -> Optional[game_entities.vent.Vent]:
        """Returns the vent on a tile if there is one."""

        for vent_ in self.vents:
            if vent_.x == x and vent_.y == y:
                return vent_
        return None

    def render_all(self, surface: Any) -> None:
        """Renders all game entities."""

        for tile_ in self.tiles:
            tile_.render(surface)

        for vent_ in self.vents:
            vent_.render(surface)

        for camera_ in self.cameras:
            camera_.render(surface)

        for trap_ in self.traps:
            trap_.render(surface)

        for item_ in self.items:
            item_.render(surface)

        for door_ in self.doors:
            door_.render(surface)

        for terminal_ in self.terminals:
            terminal_.render(surface)

        for turret_ in self.turrets:
            turret_.render(surface)

        for explosive_ in self.explosives:
            explosive_.render(surface)

        for actor_ in self.actors:
            actor_.render(surface)

    def update_all(self, game_time: int) -> None:
        """Called every tick of time to update all entities."""

        for entity_ in self.all:
            entity_.update(game_time)

    def reset(self) -> None:
        """Clears and resets all the lists."""

        self.all = []
        self.actors = []
        self.doors = []
        self.items = []

    def show_vents(self) -> None:
        """Reveals the vents and hides everything else."""

        for entity_ in self.all:
            if isinstance(entity_, game_entities.vent.Vent) or isinstance(entity_, game_entities.actor.Player):
                entity_.visible = True
            else:
                entity_.old_visible = entity_.visible  # Store the current visibility.
                entity_.visible = False

    def hide_vents(self):
        """Hides the vents and reveals everything else."""

        for entity_ in self.all:
            if isinstance(entity_, game_entities.vent.Vent) and not entity_.entrance:
                entity_.visible = False
            else:
                entity_.visible = entity_.old_visible  # In case the entity was previously invisible.
