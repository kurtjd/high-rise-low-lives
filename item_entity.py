import entity
import globals


# Returns the Item entities at a given position
def get_items_at(x, y):
    items_at_pos = []

    for item_at_pos in globals.items:
        if item_at_pos.x == x and item_at_pos.y == y:
            items_at_pos.append(item_at_pos)

    return items_at_pos


class ItemEntity(entity.Entity):
    # ~~~ PRIVATE METHODS ~~~

    def __init__(self, x, y, graphic, color, item):
        super().__init__(x, y, graphic, color)
        self.item = item
        globals.items.append(self)

    # ~~~ PUBLIC METHODS ~~~

    def actor_pick_up(self, actor):
        actor.add_inventory(self.item, 1)
        self.remove()

        return self.item

    def remove(self):
        for item in enumerate(globals.items):
            if item[1] is self:
                globals.entities.pop(item[0])

        super().remove()
