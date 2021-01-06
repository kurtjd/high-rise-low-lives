from typing import Callable
import drug_effects


class Item:
    # ~~~ PRIVATE METHODS ~~~

    def __init__(
        self,
        name: str,
        desc: str,
        throwable: bool = False,
        wieldable: bool = False
    ) -> None:
        self.name: str = name
        self.desc: str = desc
        self.throwable: bool = throwable
        self.wieldable: bool = wieldable


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
        self.damage = 80
        self.blast_radius = 3
        self.fuse = 20


class Drug(Item):
    def __init__(
        self,
        name: str,
        desc: str,
        effect: Callable[..., None]
    ) -> None:
        effects: dict = {
            "use_stitch": drug_effects.use_stitch
        }

        super().__init__(name, desc)
        self.effect = effects[effect]


class PowerSource(Item):
    def __init__(self, name: str, desc: str, charge_held: int, discharge_time: int) -> None:
        super().__init__(name, desc)

        self.discharge_time = discharge_time  # Amount of turns before self-discharges and is useless
        self.charge_held = charge_held
