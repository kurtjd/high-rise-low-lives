import item


class Weapon(item.Item):
    # ~~~ STATIC METHODS ~~~
    def __init__(self, name: str, desc: str, dmg: int, speed: int, accuracy: int) -> None:
        super().__init__(name, desc, None)
        self.dmg: int = dmg
        self.speed: int = speed
        self.accuracy: int = accuracy
