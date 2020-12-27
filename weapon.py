import item


class Weapon(item.Item):
    # ~~~ STATIC METHODS ~~~
    def __init__(self, name, desc, dmg, speed, accuracy, use_action=None):
        super().__init__(name, desc, use_action)
        self.dmg = dmg
        self.speed = speed
        self.accuracy = accuracy
