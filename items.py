from typing import Callable, Optional
import entities
import drug_effects


class Item:
    """Represents the details of an in-game item.
    Not to be confused with an ItemEntity, which represents an item being displayed in the game world,
    and has an Item object attached to it."""

    def __init__(self, name: str, desc: str) -> None:
        self.name: str = name
        self.desc: str = desc

    def on_pick_up(self, src_actor: "entities.Actor", amount: int = 1):
        """Called when the item is picked up by an actor."""

        src_actor.add_inventory(self, amount)


class Wieldable(Item):
    """Represents any item that can be wielded."""

    def __init__(self, name: str, desc: str) -> None:
        super().__init__(name, desc)


class Throwable(Item):
    """Represents any item that can be thrown."""

    def __init__(self, name: str, desc: str) -> None:
        super().__init__(name, desc)


class Weapon(Wieldable):
    """Represents any non-throwable weapon."""

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
        super().__init__(name, desc)
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


class Grenade(Throwable):
    """Represents a grenade."""

    def __init__(self, name: str, desc: str, damage: int, blast_radius: int, fuse: int) -> None:
        super().__init__(name, desc)
        self.damage = damage
        self.blast_radius = blast_radius
        self.fuse = fuse


class Drug(Item):
    """Represents a drug."""

    def __init__(self, name: str, desc: str, effect: Callable[..., None]) -> None:
        # Associate the string in the database with an actual function.
        effects: dict = {
            "use_stitch": drug_effects.use_stitch
        }

        super().__init__(name, desc)
        self.effect = effects[effect]


class PowerSource(Item):
    """Represents an item that can be used to charge up the player."""

    def __init__(self, name: str, desc: str, charge_held: int, discharge_time: int) -> None:
        super().__init__(name, desc)

        self.discharge_time = discharge_time  # Amount of turns before self-discharges and is useless
        self.charge_held = charge_held


class Cigarette(Item):
    """Represents a single unit of black-market currency."""

    def __init__(self, name: str, desc: str) -> None:
        super().__init__(name, desc)

    def on_pick_up(self, src_actor: "entities.Actor", amount: int = 1):
        """Instead of adding to the inventory, picking up a cigarette just increases the player's total."""

        src_actor.smokes += amount


class Ammo(Item):
    """Represents a single round of ammunition."""

    def __init__(self, name: str, desc: str, caliber: str, ammo_type: str):
        super().__init__(name, desc)
        self.caliber = caliber
        self.ammo_type = ammo_type
