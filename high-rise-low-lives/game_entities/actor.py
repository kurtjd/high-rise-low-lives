from __future__ import annotations
from enum import Enum, auto
from typing import Optional, Any, Callable
import databases
import interface
import items
from .entities import GameEntities
from .entity import Entity
from .item_entity import ItemEntity
from .vent import Vent
from .door import Door
from .terminal import Terminal
from .trap import Trap
from .explosive import Explosive


class Actor(Entity):
    """Represents an actor (an entity that can do things)."""

    class Action(Enum):
        """All the actions an actor can be performing."""

        NONE = auto(),
        MOVE = auto(),
        ATK_MELEE = auto(),
        ATK_RANGED = auto(),
        WIELD = auto(),
        OPEN_DOOR = auto(),
        CLOSE_DOOR = auto(),
        REST = auto(),
        PICKUP = auto(),
        HACK = auto(),
        THROW = auto(),
        USE_DRUG = auto(),
        CHARGE = auto(),
        RELOAD = auto()

    def __init__(
            self,
            name: str,
            race: str,
            class_name: str,
            desc: str,
            x: int,
            y: int,
            health: int,
            muscle: int,
            smarts: int,
            reflexes: int,
            wits: int,
            grit: int,
            ai_: Optional[Callable[..., None]],
            graphic: str,
            color: tuple[int, int, int],
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface
    ) -> None:
        super().__init__(x, y, name, desc, True, graphic, color, game_data, game_entities_, game_interface)

        # Background
        self.race: str = race
        self.class_name: str = class_name

        # Attributes
        self.muscle: int = muscle
        self.smarts: int = smarts
        self.reflexes: int = reflexes
        self.wits: int = wits
        self.grit: int = grit
        self.charm: int = 5

        # Skills
        self.hacking_skill: int = 10

        # Other stats
        self.charge_percent = 100
        self.health: int = health
        self.mp: int = 50
        self.ac: int = 6
        self.base_atk_dmg: int = 10
        self.atk_dmg: int = self.base_atk_dmg

        # Action speeds
        self.gen_speed: int = 5
        self.move_speed: int = 10
        self.atk_speed: int = 10
        self.wield_speed: int = 5
        self.hack_speed: int = 20
        self.rest_speed: int = 10
        self.throw_speed: int = 8
        self.reload_speed: int = 10
        self.recovery_rate: int = 10

        # Inventory/Equipment
        self.MAX_INVENTORY_SIZE: int = 52
        self.inventory: dict = {}
        self.wielding: Optional[items.Weapon] = None
        self.wearing: Optional[str] = None
        self.throwing: Optional[items.Item] = None
        self.smokes: int = 0

        # These properties are used to track actions.
        self.action_target: Any = None  # Used when the target isn't an x/y
        self.action_cooldown: int = -1
        self.action_target_x: int = 0
        self.action_target_y: int = 0
        self.action: Actor.Action = self.Action.NONE
        self.dest_x: int = 0
        self.dest_y: int = 0
        self.atk_target: Optional[Entity] = None
        self.bullet_path: list[tuple[int, int]] = []

        # Misc
        self.in_vents: bool = False

        # This contains a function name corresponding to one of the AI functions in ai.py
        self.ai: Callable[[Actor, list[Actor]], None] = ai_

        # If not the player, set a default action. For now, just rest.
        if not isinstance(self, Player):
            self._do_action(self.Action.REST, 1)

        game_entities_.actors.append(self)

    def _think(self) -> None:
        """Used by non-player actors to call their corresponding AI function."""

        self.ai(self, self.game_entities.actors)

    def _get_next_item_id(self) -> str:
        """Finds the correct a-zA-Z character to assign as an id to a newly acquired items."""

        # Item IDs can be a-zA-Z so loop through all ASCII numbers that match letters.
        for item_id in range(ord('a'), ord('z') + 1):
            if not chr(item_id) in self.inventory:
                return chr(item_id)
        for item_id in range(ord('A'), ord('Z') + 1):
            if not chr(item_id) in self.inventory:
                return chr(item_id)

    def _dec_item_count(self, item_id: str, amount: int = 1) -> None:
        """Decreases the amount of an item in the inventory and deletes it if zero."""

        self.inventory[item_id]["Amount"] -= amount

        if self.inventory[item_id]["Amount"] == 0:
            del self.inventory[item_id]

    def _dec_ammo_count(self, caliber: str, amount: int = 1) -> None:
        """Called when the player fires a ranged weapon and we need to decrease the correct ammo from inventory."""

        for ammo_ in self.inventory.items():
            if isinstance(ammo_[1]["Item"], items.Ammo) and ammo_[1]["Item"].caliber == caliber:
                ammo_[1]["Amount"] -= amount

                if ammo_[1]["Amount"] == 0:
                    del self.inventory[ammo_[0]]

                return

    def _die(self) -> None:
        """Called when actor's HP reaches zero."""

        self.graphic = self.game_data.tiles["CORPSE"]["Character"]
        self.color = self.game_data.tiles["CORPSE"]["Color"]
        self.blocked = self.game_data.tiles["CORPSE"]["Blocked"]
        # In future remove actor from game and replace with Corpse entity that holds actor's stats incase of revival.

        # Just quit the game for now to prevent crash.
        if isinstance(self, Player):
            raise SystemExit()

    def _recover(self) -> None:
        """Restores some stats to the actor."""

        self.health += 1
        if self.health > 100:
            self.health = 100

    def _reset_action(self) -> None:
        """Called after action cooldown has passed.
           Resets all counters and associated variables allowing for new action to be selected."""

        self.action = self.Action.NONE
        self.action_target_x = 0
        self.action_target_y = 0
        self.action_cooldown = -1  # -1 represents no action queued
        self.dest_x = 0
        self.dest_y = 0

        # Allow the AI to think of a new action.
        if not isinstance(self, Player):
            self._think()

    def _do_action(self, action: Action, cooldown: int, target_x: int = 0, target_y: int = 0) -> None:
        """Actually performs the action by calling the appropriate method."""

        # Associates a method with each action.
        actions: dict = {
            self.Action.ATK_MELEE: self._attack_melee,
            self.Action.ATK_RANGED: self._attack_ranged,
            self.Action.MOVE: self.move,
            self.Action.OPEN_DOOR: self._open_door,
            self.Action.CLOSE_DOOR: self._close_door,
            self.Action.REST: self._rest,
            self.Action.PICKUP: self._pick_up,
            self.Action.WIELD: self._wield,
            self.Action.HACK: self._hack,
            self.Action.THROW: self._throw,
            self.Action.USE_DRUG: self._use_drug,
            self.Action.CHARGE: self._charge,
            self.Action.RELOAD: self._reload
        }

        self.action = action
        self.action_cooldown = cooldown
        self.action_target_x = target_x
        self.action_target_y = target_y
        actions[action]()

    def _open_door(self) -> None:
        """Opens a door if it's not locked or if actor has key."""

        target_door: Door = self.game_entities.get_door_at(self.action_target_x, self.action_target_y)
        if not target_door.locked:
            target_door.open()
        else:
            self.game_interface.message_box.add_msg(
                f"That door is locked.", self.game_data.colors["ERROR_MSG"]
            )

    def _close_door(self) -> None:
        """Actually closes the door."""

        target_door: Door = self.game_entities.get_door_at(self.action_target_x, self.action_target_y)
        target_door.close()

    def _hack(self) -> None:
        """Attempts to hack a terminal."""

        target_terminal: Terminal = self.game_entities.get_terminal_at(
            self.action_target_x,
            self.action_target_y
        )
        target_terminal.attempt_hack(self)

    def _attack_melee(self) -> None:
        """Performs a melee attack."""

        target_actor: Actor = self.game_entities.get_actor_at(self.action_target_x, self.action_target_y)

        if target_actor is None:
            self.game_interface.message_box.add_msg(
                f"{self.name}'s attack fails!", self.game_data.colors["ERROR_MSG"]
            )
            return

        # Don't attack dead Actors
        if target_actor.health <= 0:
            return

        target_actor.receive_hit(self, self.atk_dmg, 100)

    def _attack_ranged(self) -> None:
        """Performs a ranged attack."""

        self.wielding.rounds_in_mag -= 1

        # Check each point within the bullet path for something that can be attacked.
        # If the actor is adjacent to cover and the bullet passes through the cover, subtract its cover percent from
        # the chance to hit.
        prev_entity_cover: int = 0
        for point in self.bullet_path:
            entity_at_point: Entity = self.game_entities.get_top_entity_at(point[0], point[1])
            if isinstance(entity_at_point, Actor) and entity_at_point.health > 0:
                entity_at_point.receive_hit(self, self.atk_dmg, 100 - prev_entity_cover, True)
                return
            else:
                prev_entity_cover = entity_at_point.cover_percent

            # Want to un-hardcode the character and animation delay later.
            self.render_projectile([(point[0], point[1])], ')', self.game_data.colors["RED"], 0.01)

        self.game_interface.message_box.add_msg(
            f"{self.name} shoots at nothing.", self.game_data.colors["ERROR_MSG"]
        )

    def _throw(self) -> None:
        """Throws an object."""

        # Draw the throwable as it goes through the air
        for point in self.bullet_path:
            self.render_projectile([(point[0], point[1])], ')', self.game_data.colors["RED"], 0.01)

        x: int
        y: int

        # If the player dropped a grenade at their feet:
        if not self.bullet_path:
            x = self.x
            y = self.y
        else:
            entity_at_end: Entity = self.game_entities.get_top_entity_at(
                self.bullet_path[-1][0],
                self.bullet_path[-1][1]
            )

            # If the target isn't blocked or is an Actor, place explosive exactly where thrown:
            if not entity_at_end.blocked or isinstance(entity_at_end, Actor):
                x = self.bullet_path[-1][0]
                y = self.bullet_path[-1][1]
            # If target is blocked, place explosive one point before blocked object.
            else:
                if len(self.bullet_path) > 1:
                    x = self.bullet_path[-2][0]
                    y = self.bullet_path[-2][1]
                else:
                    x = self.x
                    y = self.y

        if isinstance(self.throwing, items.Grenade):
            # Create a new explosive on the target grid cell.
            Explosive(
                x,
                y,
                self.throwing.damage,
                self.throwing.blast_radius,
                self.throwing.fuse,
                self.game_data,
                self.game_entities,
                self.game_interface
            )

    def _reload(self) -> None:
        """Reloads the currently wield firearm with the appropriate ammo."""

        mag_capacity: int = self.wielding.mag_capacity
        ammo_count: int = self.get_ammo_amount(self.wielding.caliber)

        # If the actor has more ammo in their inventory than size of mag, fill it up.
        # If not, put the actor's last ammo into the mag.
        if ammo_count >= mag_capacity:
            self.wielding.rounds_in_mag = mag_capacity
            self._dec_ammo_count(self.wielding.caliber, mag_capacity)
        elif ammo_count > 0:
            self.wielding.rounds_in_mag = ammo_count
            self._dec_ammo_count(self.wielding.caliber, ammo_count)
        else:
            return

        self.game_interface.message_box.add_msg(
            f"{self.name} reloads his {self.wielding.name}.", self.game_data.colors["SUCCESS_MSG"]
        )

    def _wield(self) -> None:
        """Update what the player is wielding and change stats to reflect that."""

        if self.action_target is None:
            self.wielding = None
            self.atk_dmg = self.base_atk_dmg
            self.game_interface.message_box.add_msg(
                f"{self.name} readies his fists.", self.game_data.colors["SUCCESS_MSG"]
            )
        else:
            self.wielding = self.action_target
            self.atk_dmg = self.base_atk_dmg + self.action_target.dmg
            self.game_interface.message_box.add_msg(
                f"{self.name} wields a {self.action_target.name}.", self.game_data.colors["SUCCESS_MSG"]
            )

            if self.wielding.distance == "RANGED":
                self._reload()

    def _use_drug(self):
        """Uses a drug."""

        drug: items.Drug = self.inventory[self.action_target]["Item"]
        drug.effect(self)

        self.game_interface.message_box.add_msg(
            f"{self.name} uses {drug.name}", self.game_data.colors["SUCCESS_MSG"]
        )

        self._dec_item_count(self.action_target)

    def _charge(self):
        """Increases charge of actor."""

        powersrc: items.PowerSource = self.inventory[self.action_target]["Item"]
        self.charge_percent += powersrc.charge_held

        self.game_interface.message_box.add_msg(
            f"{self.name} receives {powersrc.charge_held}% charge from a {powersrc.name}.",
            self.game_data.colors["SUCCESS_MSG"]
        )

        self._dec_item_count(self.action_target)

    def _rest(self) -> None:
        """'Rests' by just doing nothing."""

        pass

    def _pick_up(self) -> None:
        """Actually picks up an items."""

        # Get all items at target and ask which to pick-up
        # For now just pick up first item
        items_: list[ItemEntity] = self.game_entities.get_items_at(
            self.action_target_x,
            self.action_target_y
        )
        item = items_[0].actor_pick_up(self)

        self.game_interface.message_box.add_msg(
            f"{self.name} picks up a {item.name}.", self.game_data.colors["SUCCESS_MSG"]
        )

    def add_inventory(self, item_: items.Item, amount: int = 1) -> None:
        """Adds an item to the inventory"""

        self.inventory[self._get_next_item_id()] = {"Item": item_, "Amount": amount}

    def get_wieldable_items(self) -> [items.Wieldable]:
        """Returns a list of items in the actor's inventory that can be wielded."""

        return [item_ for item_ in self.inventory.items() if isinstance(item_[1]["Item"], items.Wieldable)]

    def get_throwable_items(self) -> [items.Throwable]:
        """Returns a list of items in the actor's inventory that can be thrown."""

        return [item_ for item_ in self.inventory.items() if isinstance(item_[1]["Item"], items.Throwable)]

    def get_drug_items(self) -> [items.Drug]:
        """Returns a list of drugs in the actor's inventory."""

        return [item_ for item_ in self.inventory.items() if isinstance(item_[1]["Item"], items.Drug)]

    def get_power_sources(self) -> [items.PowerSource]:
        """Returns a list of power sources in the actor's inventory."""

        return [item_ for item_ in self.inventory.items() if isinstance(item_[1]["Item"], items.PowerSource)]

    def get_ammo_amount(self, caliber: str) -> int:
        """Returns how much ammo of a given caliber the actor has in inventory."""

        total_amount = 0
        for ammo_ in self.inventory.items():
            if isinstance(ammo_[1]["Item"], items.Ammo) and ammo_[1]["Item"].caliber == caliber:
                total_amount += ammo_[1]["Amount"]

        return total_amount

    def receive_hit(
            self,
            src_entity: Entity,
            atk_dmg: int,
            hit_chance: int,
            ranged: bool = False
    ) -> None:
        """Called by anything that wants to damage this actor."""

        # Eventually do a bunch of calculations to see if hit actually lands.
        if hit_chance:
            pass

        self.health -= atk_dmg

        # Send different message depending on what is attacked with.
        # Change color depending on if player or not.
        msg_color: tuple[int, int, int]
        hit_msg: str
        if isinstance(src_entity, Player):
            msg_color = self.game_data.colors["ATK_MSG"]
        else:
            msg_color = self.game_data.colors["BAD_MSG"]

        if self.health > 0:
            if isinstance(src_entity, Actor):
                if ranged:
                    hit_msg = (
                        f"{src_entity.name} shoots {self.name} with his"
                        f" {src_entity.wielding.name} for {atk_dmg} damage!"
                    )
                elif src_entity.wielding is not None:
                    hit_msg = (
                        f"{src_entity.name} hits {self.name} with his {src_entity.wielding.name} for {atk_dmg} damage!"
                    )
                else:
                    hit_msg = (
                        f"{src_entity.name} pummels {self.name} with his fists for {atk_dmg} damage!"
                    )
            elif isinstance(src_entity, Explosive):
                hit_msg = f"{self.name} is caught in an explosion and receives {atk_dmg} damage!"
            else:
                hit_msg = "LOL"
        else:
            if isinstance(src_entity, Actor):
                if ranged:
                    hit_msg = f"{src_entity.name} executes {self.name}."
                else:
                    hit_msg = f"{src_entity.name} guts {self.name}."
            elif isinstance(src_entity, Explosive):
                hit_msg = f"An explosive turns {self.name} into a thick red paste."
            else:
                hit_msg = "LOL"

            msg_color = self.game_data.colors["KILL_MSG"]

            self._die()

        self.game_interface.message_box.add_msg(hit_msg, msg_color)

    def move(self) -> None:
        """Moves the actor to a new position."""

        # We need to check again that the destination isn't blocked in case something moved there in the meantime.
        for dest_entity in self.game_entities.get_all_at(self.dest_x, self.dest_y):
            if dest_entity.blocked:
                if isinstance(self, Player):
                    self.game_interface.message_box.add_msg(
                        f"{self.name} slams into something.", self.game_data.colors["ERROR_MSG"]
                    )
                return

        self.x = self.dest_x
        self.y = self.dest_y

    def attempt_atk(
            self,
            x: int,
            y: int,
            ranged: bool = False,
            bullet_path: Optional[list[tuple[int, int]]] = None
    ) -> None:
        """Perform some checks before actually attacking."""

        if not ranged:
            self._do_action(self.Action.ATK_MELEE, self.atk_speed, x, y)
        else:
            if self.wielding is not None and self.wielding.distance == "RANGED":
                # Does the weapon have rounds in the mag?
                if self.wielding.rounds_in_mag > 0:
                    self.bullet_path = bullet_path
                    self._do_action(self.Action.ATK_RANGED, self.atk_speed, x, y)
                else:
                    if isinstance(self, Player):
                        self.game_interface.message_box.add_msg(
                            f"You are out of ammo! Try reloading.", self.game_data.colors["ERROR_MSG"]
                        )
            elif isinstance(self, Player):
                # Is the player not wielding a ranged weapon?
                self.game_interface.message_box.add_msg(
                    f"You are not wielding a ranged weapon.", self.game_data.colors["ERROR_MSG"]
                )

    def attempt_move(self, x: int, y: int) -> bool:
        """Perform some checks before moving."""

        # The destination the actor is attempting to move to
        new_x: int = self.x + x
        new_y: int = self.y + y
        self.dest_x = new_x
        self.dest_y = new_y

        # We want to check what entites are occupying the move destination if not in the vents.
        # Do different things depending on what's there.
        if not self.in_vents:
            dest_entities: list[Entity] = self.game_entities.get_all_at(new_x, new_y)
            for dest_entity in dest_entities:
                # Check to see if destination has an Actor, if so perform melee attack
                if isinstance(dest_entity, Actor) and dest_entity.health > 0:
                    self.attempt_atk(new_x, new_y)
                    return True
                elif isinstance(dest_entity, Door) and not dest_entity.opened:
                    self._do_action(self.Action.OPEN_DOOR, self.gen_speed, new_x, new_y)
                    return True
                elif isinstance(dest_entity, Terminal):
                    self._do_action(self.Action.HACK, self.hack_speed, new_x, new_y)
                    return True
                elif isinstance(dest_entity, Vent) and not isinstance(self, Player):
                    return False  # Don't let NPCs follow player into vents

                # Prevent from moving into blocked entity.
                elif dest_entity.blocked:
                    return False

        # If destination is not blocked and is not a living Actor, move to it
        self._do_action(self.Action.MOVE, self.move_speed)
        return True

    def attempt_throw(self, x: int, y: int, item: items.Item, throw_path: Optional[list[tuple[int, int]]] = None):
        """Perform some checks before throwing item."""

        self.bullet_path = throw_path
        self.throwing = item
        self._do_action(self.Action.THROW, self.throw_speed, x, y)

    def attempt_pickup(self) -> None:
        """Perform some checks before picking up item."""

        # Only pick up if there's something on the floor.
        if self.game_entities.get_items_at(self.x, self.y):
            self._do_action(self.Action.PICKUP, self.gen_speed, self.x, self.y)
        elif isinstance(self, Player):
            self.game_interface.message_box.add_msg(
                "There's nothing here to pickup.", self.game_data.colors["ERROR_MSG"]
            )

    def attempt_wield(self, new_weapon: Optional[items.Item]) -> None:
        """Perform some checks before wielding weapon."""

        # Make sure attempting to wield an actual weapon.
        # Include None because that is fists.
        if (new_weapon is not None and not isinstance(new_weapon, items.Weapon)) and isinstance(self, Player):
            self.game_interface.message_box.add_msg(
                f"{self.name} cannot wield a {new_weapon.name}.", self.game_data.colors["ERROR_MSG"]
            )
            return

        self.action_target = new_weapon
        self._do_action(self.Action.WIELD, self.wield_speed)

    def attempt_use_drug(self, drug_id: str) -> None:
        """Perform some checks before using drug."""

        self.action_target = drug_id
        self._do_action(self.Action.USE_DRUG, self.gen_speed)

    def attempt_charge(self, powersrc_id: str) -> None:
        """Perform some checks before charging up."""

        self.action_target = powersrc_id
        self._do_action(self.Action.CHARGE, self.gen_speed)

    def attempt_reload(self) -> None:
        """Perform some checks before reloading."""

        if not isinstance(self.wielding, items.Weapon) or self.wielding.distance != "RANGED":
            self.game_interface.message_box.add_msg(
                "You can't reload your current weapon.",
                self.game_data.colors["ERROR_MSG"]
            )
        elif self.wielding.rounds_in_mag == self.wielding.mag_capacity:
            self.game_interface.message_box.add_msg(
                "Your magazine is already full.",
                self.game_data.colors["ERROR_MSG"]
            )
        elif not self.get_ammo_amount(self.wielding.caliber):
            self.game_interface.message_box.add_msg(
                "You have no more ammo to reload with.",
                self.game_data.colors["ERROR_MSG"]
            )
        else:
            self._do_action(self.Action.RELOAD, self.reload_speed)

    def attempt_close_door(self) -> None:
        """Checks for open doors around the Actor and closes them if they exist."""

        for x in range(-1, 2):
            for y in range(-1, 2):
                if x != 0 or y != 0:
                    target_door: Door = self.game_entities.get_door_at(self.x + x, self.y + y)
                    if target_door is not None and target_door.opened:
                        self._do_action(self.Action.CLOSE_DOOR, self.gen_speed, target_door.x, target_door.y)
                        return

        if isinstance(self, Player):
            self.game_interface.message_box.add_msg(
                "There's no door to be closed here.", self.game_data.colors["ERROR_MSG"]
            )

    def attempt_rest(self) -> None:
        """Performs some checks before resting."""

        self._do_action(self.Action.REST, self.rest_speed)

    def update(self, game_time: int) -> None:
        """Update the actor."""

        # Do nothing if dead.
        if self.health <= 0:
            return

        # Check if time to recover
        if game_time > 0 and (game_time % self.recovery_rate) == 0:
            self._recover()

        # If actor is still in cooldown from previous action, decrease cooldown.
        if self.action_cooldown > 0:
            self.action_cooldown -= 1

            # Reset action counters allowing for new action to be selected.
            if self.action_cooldown == 0:
                self._reset_action()


class Player(Actor):
    """Represents the player character."""

    def __init__(
            self,
            name: str,
            race: str,
            class_name: str,
            desc: str,
            x: int,
            y: int,
            health: int,
            muscle: int,
            smarts: int,
            reflexes: int,
            wits: int,
            grit: int,
            graphic: str,
            color: tuple[int, int, int],
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface
    ) -> None:
        super().__init__(name, race, class_name, desc, x, y, health, muscle, smarts, reflexes, wits, grit,
                         None, graphic, color, game_data, game_entities_, game_interface)

        self.examine_target: Any = None  # What the player selected to examine.
        self.item_selected: Optional[items.Item] = None  # What the player has selected from inventory to be used.

        self.max_charge_loss_delay: int = 100  # The number of turns before losing a percent of charge.
        self.charge_loss_delay = self.max_charge_loss_delay

        self.vent_speed_multi = 2

        game_entities_.player = self

    def move(self) -> None:
        """Moves the player."""

        super().move()

        # If the player moves into or out of vents, change what is visible.
        vent_: Vent = self.game_entities.get_vent_at(self.x, self.y)
        if vent_ is not None:
            if not self.in_vents:
                self.game_entities.show_vents()
                self.in_vents = True
                self.move_speed *= self.vent_speed_multi
            elif vent_.entrance:
                self.game_entities.hide_vents()
                self.in_vents = False
                self.move_speed /= self.vent_speed_multi
        elif self.in_vents:
            self.game_entities.hide_vents()
            self.in_vents = False
            self.move_speed /= self.vent_speed_multi

        # If the player walks onto a trap, trigger it.
        trap_: Trap = self.game_entities.get_trap_at(self.x, self.y)
        if trap_ is not None:
            trap_.trigger()

    def attempt_move(self, x: int, y: int) -> bool:
        """Does some checks before actually letting the player move."""

        # The destination the player is attempting to move to
        new_x: int = self.x + x
        new_y: int = self.y + y

        # If the player is in the vents, make it so they can't move through un-blocked entities like floors.
        vent_to: Vent = self.game_entities.get_vent_at(new_x, new_y)
        vent_on: Vent = self.game_entities.get_vent_at(self.x, self.y)

        if self.in_vents and vent_to is None and vent_on is not None and not vent_on.entrance:
            return False

        if not self.in_vents and \
                ((vent_to is not None and not vent_to.entrance) and (vent_on is None or not vent_on.entrance)):
            return False

        super().attempt_move(x, y)

    def update(self, game_time: int) -> None:
        """Updates the player."""

        super().update(game_time)

        # Decreases the player's charge as time goes on.
        self.charge_loss_delay -= 1

        if self.charge_loss_delay == 0:
            self.charge_percent -= 1
            self.charge_loss_delay = self.max_charge_loss_delay
