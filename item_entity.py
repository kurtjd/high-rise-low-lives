import entity
import item
import actor
import game_entities


class ItemEntity(entity.Entity):
    # ~~~ PRIVATE METHODS ~~~

    def __init__(
            self,
            x: int,
            y: int,
            name: str,
            desc: str,
            graphic: str,
            color: tuple[int, int, int],
            item_: item.Item,
            game_entities_: "game_entities.GameEntities"
    ) -> None:
        super().__init__(x, y, name, desc, False, graphic, color, game_entities_)
        self.item: item.Item = item_
        game_entities_.items.append(self)

    # ~~~ PUBLIC METHODS ~~~

    def actor_pick_up(self, actor_: "actor.Actor") -> item.Item:
        actor_.add_inventory(self.item, 1)
        self.remove()

        return self.item

    def remove(self) -> None:
        game_items: list[ItemEntity] = self.game_entities.items
        for item_ in enumerate(game_items):
            if item_[1] is self:
                game_items.pop(item_[0])

        super().remove()
