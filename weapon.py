import item


class Weapon(item.Item):
    # ~~~ STATIC METHODS ~~~
    def __init__(self, name, desc, dmg, speed, accuracy):
        super().__init__(name, desc, None)
        self.dmg = dmg
        self.speed = speed
        self.accuracy = accuracy
