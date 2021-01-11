from __future__ import annotations
import databases
import interface
import items
from .entity import Entity
from .actor import Actor


class ItemEntity(Entity):
    """Represents an item entity, not to be confused with an actual item."""

    def __init__(
            self,
            x: int,
            y: int,
            name: str,
            desc: str,
            graphic: str,
            color: tuple[int, int, int],
            item_: items.Item,
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface
    ) -> None:
        super().__init__(x, y, name, desc, False, graphic, color, game_data, game_entities_, game_interface)

        self.item: items.Item = item_  # The actual item this entity represents.

        game_entities_.items.append(self)

    def actor_pick_up(self, actor_: Actor, amount: int = 1) -> items.Item:
        """Called when the actor picks up the item entity."""

        self.item.on_pick_up(actor_, amount)
        self.remove()

        return self.item

    def remove(self) -> None:
        """Removes the item entity from the list of all item entities."""

        game_items: list[ItemEntity] = self.game_entities.items
        for item_ in enumerate(game_items):
            if item_[1] is self:
                game_items.pop(item_[0])

        super().remove()
