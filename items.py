from typing import Callable, Optional
import entities
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

    def on_pick_up(self, src_actor: "entities.Actor", amount: int = 1):
        src_actor.add_inventory(self, amount)


class Weapon(Item):
    # ~~~ STATIC METHODS ~~~
    def __init__(
            self,
            name: str,
            desc: str,
            dmg: int,
            speed: int,
            accuracy: int,
            distance: str,
            weapon_type: str,
            hands: int,
            caliber: Optional[str] = None,
            mag_capacity: Optional[int] = None
    ) -> None:
        super().__init__(name, desc, False, True)
        self.dmg: int = dmg
        self.speed: int = speed
        self.accuracy: int = accuracy
        self.distance: str = distance
        self.weapon_type: str = weapon_type
        self.hands: int = hands

        # Pertains to ranged only
        self.caliber: str = caliber
        self.mag_capacity: int = mag_capacity
        self.rounds_in_mag: int = 0


class Grenade(Item):
    def __init__(
        self,
        name: str,
        desc: str,
        damage: int,
        blast_radius: int,
        fuse: int
    ) -> None:
        super().__init__(name, desc, True, False)
        self.damage = damage
        self.blast_radius = blast_radius
        self.fuse = fuse


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


class Cigarette(Item):
    def __init__(self, name: str, desc: str) -> None:
        super().__init__(name, desc)

    def on_pick_up(self, src_actor: "entities.Actor", amount: int = 1):
        src_actor.smokes += amount


class Ammo(Item):
    def __init__(self, name: str, desc: str, caliber: str, ammo_type: str):
        super().__init__(name, desc)
        self.caliber = caliber
        self.ammo_type = ammo_type
