from typing import Any, Optional


class Item:
    # ~~~ PRIVATE METHODS ~~~

    def __init__(self, name: str, desc: str, use_action: Optional[Any] = None) -> None:
        self.name: str = name
        self.desc: str = desc
        self.use_action: Any = use_action


class Weapon(Item):
    # ~~~ STATIC METHODS ~~~
    def __init__(self, name: str, desc: str, dmg: int, speed: int, accuracy: int) -> None:
        super().__init__(name, desc, None)
        self.dmg: int = dmg
        self.speed: int = speed
        self.accuracy: int = accuracy
