import entity


class ItemEntity(entity.Entity):
    # ~~~ PRIVATE METHODS ~~~

    def __init__(self, x, y, graphic, color, item, game_entities):
        super().__init__(x, y, False, graphic, color, game_entities)
        self.item = item
        self.game_items = game_entities.items
        game_entities.items.append(self)

    # ~~~ PUBLIC METHODS ~~~

    def actor_pick_up(self, actor):
        actor.add_inventory(self.item, 1)
        self.remove()

        return self.item

    def remove(self):
        for item in enumerate(self.game_items):
            if item[1] is self:
                self.game_items.pop(item[0])

        super().remove()
