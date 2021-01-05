from typing import Any


class Item:
    # ~~~ PRIVATE METHODS ~~~

    def __init__(
        self,
        name: str,
        desc: str,
        throwable: bool = False,
        wieldable: bool = False,
        use_action: Any = None
    ) -> None:
        self.name: str = name
        self.desc: str = desc
        self.throwable: bool = throwable
        self.wieldable: bool = wieldable
        self.use_action: Any = use_action


class Weapon(Item):
    # ~~~ STATIC METHODS ~~~
    def __init__(self, name: str, desc: str, dmg: int, speed: int, accuracy: int) -> None:
        super().__init__(name, desc, False, True)
        self.dmg: int = dmg
        self.speed: int = speed
        self.accuracy: int = accuracy


class Grenade(Item):
    def __init__(
        self,
        name: str,
        desc: str
    ) -> None:
        super().__init__(name, desc, True, False)
