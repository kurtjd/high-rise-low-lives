import math
import time
from enum import Enum, auto
from typing import Optional, Callable, Any
import rendering
import databases
import interface
import items
import ai
import bresenham


class GameEntities:
    """Stores and manages the lists of different game entities."""

    def __init__(self, window: Any, surface: Any) -> None:
        self.all: list[Entity] = []
        self.tiles: list[Tile] = []
        self.actors: list[Actor] = []
        self.turrets: list[Turret] = []
        self.doors: list[Door] = []
        self.items: list[ItemEntity] = []
        self.terminals: list[Terminal] = []
        self.cameras: list[Camera] = []
        self.traps: list[Trap] = []
        self.vents: list[Vent] = []
        self.explosives: list[Explosive] = []
        self.player: Optional[Player] = None

        self.window: Any = window
        self.surface: Any = surface

    def get_all_at(self, x: int, y: int) -> list["Entity"]:
        """Returns all the entities on a tile."""

        return [entity_ for entity_ in self.all if entity_.x == x and entity_.y == y]

    def get_top_entity_at(self, x: int, y: int, ignore_invis: bool = False) -> Optional["Entity"]:
        """Returns the top-most entity on a tile."""

        if not ignore_invis:
            return self.get_all_at(x, y)[-1]
        else:
            # Get the top-most entity that is visible.
            all_: list[Entity] = self.get_all_at(x, y)
            all_.reverse()
            for entity in all_:
                if entity.visible:
                    return entity
            return all_[0]  # If no visible entities at position, return the top invisible one anyway.

    def get_actor_at(self, x: int, y: int) -> Optional["Actor"]:
        """Returns the actor on a tile if there is one."""

        for actor_ in self.actors:
            if actor_.x == x and actor_.y == y:
                return actor_
        return None

    def get_door_at(self, x: int, y: int) -> Optional["Door"]:
        """Returns the door on a tile if there is one."""

        for door_ in self.doors:
            if door_.x == x and door_.y == y:
                return door_
        return None

    def get_items_at(self, x: int, y: int) -> list["ItemEntity"]:
        """Returns all the item entities on a tile."""

        return [item_ for item_ in self.items if item_.x == x and item_.y == y]

    def get_terminal_at(self, x: int, y: int) -> Optional["Terminal"]:
        """Returns the terminal on a tile if there is one."""

        for terminal_ in self.terminals:
            if terminal_.x == x and terminal_.y == y:
                return terminal_
        return None

    def get_trap_at(self, x: int, y: int) -> Optional["Trap"]:
        """Returns the trap on a tile if there is one."""

        for trap_ in self.traps:
            if trap_.x == x and trap_.y == y:
                return trap_
        return None

    def get_vent_at(self, x: int, y: int) -> Optional["Vent"]:
        """Returns the vent on a tile if there is one."""

        for vent_ in self.vents:
            if vent_.x == x and vent_.y == y:
                return vent_
        return None

    def render_all(self, surface: Any) -> None:
        """Renders all game entities."""

        for tile_ in self.tiles:
            tile_.render(surface)

        for vent_ in self.vents:
            vent_.render(surface)

        for camera_ in self.cameras:
            camera_.render(surface)

        for trap_ in self.traps:
            trap_.render(surface)

        for item_ in self.items:
            item_.render(surface)

        for door_ in self.doors:
            door_.render(surface)

        for terminal_ in self.terminals:
            terminal_.render(surface)

        for turret_ in self.turrets:
            turret_.render(surface)

        for explosive_ in self.explosives:
            explosive_.render(surface)

        for actor_ in self.actors:
            actor_.render(surface)

    def update_all(self, game_time: int) -> None:
        """Called every tick of time to update all entities."""

        for entity_ in self.all:
            entity_.update(game_time)

    def reset(self) -> None:
        """Clears and resets all the lists."""

        self.all = []
        self.actors = []
        self.doors = []
        self.items = []

    def show_vents(self) -> None:
        """Reveals the vents and hides everything else."""

        for entity in self.all:
            if isinstance(entity, Vent) or isinstance(entity, Player):
                entity.visible = True
            else:
                entity.old_visible = entity.visible  # Store the current visibility.
                entity.visible = False

    def hide_vents(self):
        """Hides the vents and reveals everything else."""

        for entity in self.all:
            if isinstance(entity, Vent) and not entity.entrance:
                entity.visible = False
            else:
                entity.visible = entity.old_visible  # In case the entity was previously invisible.


class Entity:
    """Represents any game entity."""

    def __init__(
            self,
            x: int,
            y: int,
            name: str,
            desc: str,
            blocked: bool,
            graphic: str,
            color: Optional[tuple[int, int, int]],
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface,
            cover_percent: int = 0,
            visible: bool = True
    ) -> None:
        self.x: int = x
        self.y: int = y
        self.name: str = name
        self.desc: str = desc
        self.old_graphic = graphic
        self.graphic: str = graphic
        self.color: Optional[tuple[int, int, int]] = color
        self.bgcolor: Optional[tuple[int, int, int]] = None
        self.blocked: bool = blocked
        self.old_visible: bool = visible
        self.visible: bool = visible
        self.noise_level: int = 0
        self.cover_percent = cover_percent

        self.game_data: databases.Databases = game_data
        self.game_interface: interface.Interface = game_interface
        self.game_entities: GameEntities = game_entities_

        game_entities_.all.append(self)

    def render(self, surface: Any) -> None:
        """Renders the entity."""

        if self.visible:
            rendering.render(surface, self.graphic, self.x, self.y, self.color, self.bgcolor)

    def update(self, game_time: int) -> None:
        """Updates the entity."""
        pass

    def remove(self) -> None:
        """Removes the entity from the list of all entities."""

        for entity_ in enumerate(self.game_entities.all):
            if entity_[1] is self:
                self.game_entities.all.pop(entity_[0])

    def make_noise(self, noise_radius: int) -> None:
        """Causes this entity to make noise."""
        self.noise_level = noise_radius

    def highlight(self, color: Optional[tuple[int, int, int]]):
        """Highlights this entity by setting it's background color.
           If the tile is invisible, do some stuff to still get a highlight of it."""

        self.bgcolor = color

        if self.visible:
            if color is None:
                self.visible = self.old_visible
                self.graphic = self.old_graphic
        else:
            if color is not None:
                self.old_visible = self.visible
                self.old_graphic = self.graphic
                self.graphic = ' '
                self.visible = True

    def get_line_of_sight(
            self,
            x2: int,
            y2: int,
            extend: bool = False,
            ignore_cover: bool = True
    ) -> list[tuple[int, int]]:
        """Uses the bresenham line algorithm to get a list of points on the map the LOS would pass through."""

        end_x: int = x2
        end_y: int = y2

        # Extend the path beyond where entity selected using slope of line.
        if extend:
            end_x = x2 + ((x2 - self.x) * 20)  # 20 is arbitrary number for max LOS range.
            end_y = y2 + ((y2 - self.y) * 20)

        # Disclude the entity from the LOS.
        los: list[tuple[int, int]] = bresenham.bresenham((self.x, self.y), (end_x, end_y))[1:]

        # Check each point in the LOS if it's 100% cover (basically meaning it's a wall). If so, stop the LOS there.
        final_los: list[tuple[int, int]] = []
        for point in los:
            final_los.append(point)
            for entity in self.game_entities.get_all_at(point[0], point[1]):
                if entity.cover_percent == 100 or (not ignore_cover and entity.blocked):
                    return final_los

        return final_los

    def render_projectile(
            self,
            points: list[tuple[int, int]],
            char: str,
            color: tuple[int, int, int],
            delay: float
    ) -> None:
        """'Animates' a projectile as it flies through the air by sleeping briefly between renders."""

        self.game_entities.render_all(self.game_entities.surface)
        for point in points:
            rendering.render(self.game_entities.surface, char, point[0], point[1], color)
        self.game_entities.window.present(self.game_entities.surface)
        time.sleep(delay)

    def compute_fov(self, radius: int, ignore_cover: bool = True) -> list[tuple[int, int]]:
        """Computes all seeable points in a radius from the entity by casting a line along the circumference
        of the radius and seeing if the line hits any blocked objects."""

        top: int = self.y - radius
        bottom: int = self.y + radius
        left: int = self.x - radius
        right: int = self.x + radius

        # Gets each point along the circumference of the circle formed by the radius
        circ_points: list[tuple[int, int]] = []
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                distance: float = math.dist((x, y), (self.x, self.y))

                if 0.0 <= (radius - distance) < 1.0:
                    circ_points.append((x, y))

        # Now calculate the line-of-sight to each point along the circumference to check if anything is blocking view
        fov: list[tuple[int, int]] = []
        for circ_point in circ_points:
            los: list[tuple[int, int]] = self.get_line_of_sight(circ_point[0], circ_point[1], False, ignore_cover)
            for los_point in los:
                fov.append(los_point)

        return fov


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

    def receive_hit(self, src_entity: Entity, atk_dmg: int, hit_chance: int, ranged: bool = False) -> None:
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
        vent: Vent = self.game_entities.get_vent_at(self.x, self.y)
        if vent is not None:
            if not self.in_vents:
                self.game_entities.show_vents()
                self.in_vents = True
                self.move_speed *= self.vent_speed_multi
            elif vent.entrance:
                self.game_entities.hide_vents()
                self.in_vents = False
                self.move_speed /= self.vent_speed_multi
        elif self.in_vents:
            self.game_entities.hide_vents()
            self.in_vents = False
            self.move_speed /= self.vent_speed_multi

        # If the player walks onto a trap, trigger it.
        trap: Trap = self.game_entities.get_trap_at(self.x, self.y)
        if trap is not None:
            trap.trigger()

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


class Turret(Actor):
    """Represents a turret."""

    def __init__(
            self,
            x: int,
            y: int,
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface
    ):
        self.turret_data: dict = game_data.npcs["TURRET"]
        self.disabled: bool = False
        self.friendly_fire: bool = False

        super().__init__(
            self.turret_data["Name"],
            self.turret_data["Race"],
            self.turret_data["Class"],
            self.turret_data["Description"],
            x,
            y,
            100,
            self.turret_data["Muscle"],
            self.turret_data["Smarts"],
            self.turret_data["Reflexes"],
            self.turret_data["Wits"],
            self.turret_data["Grit"],
            ai.turret,
            self.turret_data["Graphic"],
            self.turret_data["Color"],
            game_data,
            game_entities_,
            game_interface
        )

        self.game_entities.turrets.append(self)


class ItemEntity(Entity):
    """Represents an item entity, not to be confused with an actual item."""

    def __init__(
            self,
            x: int,
            y: int,
            name: str,
            desc: str,
            graphic: str,
            color: tuple[int, int, int],
            item_: items.Item,
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface
    ) -> None:
        super().__init__(x, y, name, desc, False, graphic, color, game_data, game_entities_, game_interface)

        self.item: items.Item = item_  # The actual item this entity represents.

        game_entities_.items.append(self)

    def actor_pick_up(self, actor_: Actor, amount: int = 1) -> items.Item:
        """Called when the actor picks up the item entity."""

        self.item.on_pick_up(actor_, amount)
        self.remove()

        return self.item

    def remove(self) -> None:
        """Removes the item entity from the list of all item entities."""

        game_items: list[ItemEntity] = self.game_entities.items
        for item_ in enumerate(game_items):
            if item_[1] is self:
                game_items.pop(item_[0])

        super().remove()


class Tile(Entity):
    """Represents a static tile on the game map."""

    def __init__(
            self,
            x: int,
            y: int,
            name: str,
            desc: str,
            blocked: bool,
            graphic: str,
            color: tuple[int, int, int],
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface,
            cover_percent: int = 0,
            visible: bool = True
    ) -> None:
        super().__init__(
            x,
            y,
            name,
            desc,
            blocked,
            graphic,
            color,
            game_data,
            game_entities_,
            game_interface,
            cover_percent,
            visible
        )

        game_entities_.tiles.append(self)


class Vent(Tile):
    """Represents a vent."""

    def __init__(
            self,
            x: int,
            y: int,
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface,
            entrance: bool = False
    ) -> None:
        self.entrance: bool = entrance  # Whether or not this is an entrance vent.
        visible: bool = True
        tile: dict

        if self.entrance:
            tile = game_data.tiles["VENT_ENTER"]
        else:
            tile = game_data.tiles["VENT"]
            visible = False

        super().__init__(
            x,
            y,
            tile["Name"],
            tile["Desc"],
            tile["Blocked"],
            tile["Character"],
            tile["Color"],
            game_data,
            game_entities_,
            game_interface,
            tile["Cover Percent"],
            visible
        )

        game_entities_.vents.append(self)


class Door(Entity):
    """Represents a door"""

    def __init__(
            self,
            x: int,
            y: int,
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface
    ) -> None:
        tile: dict = game_data.tiles["DOOR_CLOSED"]

        super().__init__(
            x,
            y,
            tile["Name"],
            tile["Desc"],
            tile["Blocked"],
            tile["Character"],
            tile["Color"],
            game_data,
            game_entities_,
            game_interface,
            tile["Cover Percent"]
        )
        self.opened: bool = False
        self.locked: bool = False

        game_entities_.doors.append(self)

    def open(self) -> None:
        """Changes the appearance of the door and makes it no longer blocked."""

        self.opened = True
        self.blocked = False
        self.graphic = self.game_data.tiles["DOOR_OPEN"]["Character"]
        self.color = self.game_data.tiles["DOOR_OPEN"]["Color"]
        self.cover_percent = self.game_data.tiles["DOOR_OPEN"]["Cover Percent"]

    def close(self) -> None:
        """Changes the appearance of the door and makes it blocked."""

        self.opened = False
        self.blocked = True
        self.graphic = self.game_data.tiles["DOOR_CLOSED"]["Character"]
        self.color = self.game_data.tiles["DOOR_CLOSED"]["Color"]
        self.cover_percent = self.game_data.tiles["DOOR_CLOSED"]["Cover Percent"]


class Terminal(Entity):
    """ Terminals can be hacked to do things like:
         open doors, turn off security cameras, disable turrets and traps, download programs, etc
         If failed to hack, can do nasty things like sound an alarm, explode, give you a virus, etc """

    class SuccessResult(Enum):
        """All the good things that can happen upon a successful hack."""

        DISABLE_CAMS: int = auto(),
        DISABLE_TURRETS: int = auto(),
        UNLOCK_DOORS: int = auto()

    class FailResult(Enum):
        """All the bad things that can happen upon a failed hack."""

        SOUND_ALARM: int = auto(),
        EXPLODE: int = auto()

    def __init__(
            self,
            x: int,
            y: int,
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface
    ) -> None:
        tile: dict = game_data.tiles["TERMINAL"]

        super().__init__(x, y, tile["Name"], tile["Desc"], tile["Blocked"],
                         tile["Character"], tile["Color"], game_data, game_entities_, game_interface)

        self.difficulty: int = 0
        self.success_results: list[int] = []
        self.fail_results: list[int] = []
        self._choose_results()

        game_entities_.terminals.append(self)

    def _choose_results(self) -> None:
        """This will eventually decide randomly which and how many success/fail results to generate for this terminal.
           The number of success will increase difficulty and the higher the difficulty the more number of fails."""

        self.success_results.append(self.SuccessResult.UNLOCK_DOORS)
        self.fail_results.append(self.FailResult.SOUND_ALARM)
        self.difficulty = 5

    def _unlock_doors(self) -> None:
        """Unlocks all doors on the current floor."""

        for door in self.game_entities.doors:
            door.locked = False

        self.game_interface.message_box.add_msg(
            f"All doors unlocked.", self.game_data.colors["SYS_MSG"]
        )

    def _sound_alarm(self) -> None:
        """Sounds an alarm by generating a lot of noise."""

        self.make_noise(999)
        self.game_interface.message_box.add_msg(
            f"Alarms sounded.", self.game_data.colors["SYS_MSG"]
        )

    def _success_hack(self, actor_: Actor) -> None:
        """Calls all the success functions associated with this terminal."""

        self.game_interface.message_box.add_msg(
            f"{actor_.name} successfully hacks the terminal.", self.game_data.colors["SUCCESS_MSG"]
        )

        for result in self.success_results:
            if result == self.SuccessResult.UNLOCK_DOORS:
                self._unlock_doors()

    def _fail_hack(self, actor_: Actor) -> None:
        """Calls all the fail functions associated with this terminal."""

        self.game_interface.message_box.add_msg(
            f"{actor_.name} fails to hack the terminal.", self.game_data.colors["BAD_MSG"]
        )

        for result in self.fail_results:
            if result == self.FailResult.SOUND_ALARM:
                self._sound_alarm()

    def attempt_hack(self, actor_: Actor) -> None:
        """Called by an actor that wants to attempt to hack the terminal."""

        if actor_.hacking_skill > self.difficulty:
            self._success_hack(actor_)
        else:
            self._fail_hack(actor_)


class Camera(Entity):
    """Represents a security camera."""

    def __init__(
            self,
            x: int,
            y: int,
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface
    ) -> None:
        tile: dict = game_data.tiles["CAMERA"]
        super().__init__(
            x,
            y,
            tile["Name"],
            tile["Desc"],
            tile["Blocked"],
            tile["Character"],
            tile["Color"],
            game_data,
            game_entities_,
            game_interface
        )

        self.radius: int = 4
        self.fov: list[tuple[int, int]] = self.compute_fov(self.radius)

        self.triggered: bool = False  # If the player triggered this camera to sound alarms

        self.game_entities.cameras.append(self)

    def update(self, game_time: int) -> None:
        """Updates the camera."""

        if not self.triggered:
            # Check if player is within FOV, if so sound alarms by making a lot of noise.
            # Eventually also do stealth check.
            for point in self.fov:
                if point[0] == self.game_entities.player.x and point[1] == self.game_entities.player.y:
                    self.triggered = True
                    self.game_interface.message_box.add_msg(
                        f"You've been spotted! Alarms sounded!", self.game_data.colors["SYS_MSG"]
                    )
                    break

        if self.triggered:
            self.make_noise(999)


class Trap(Entity):
    """Represents a trap."""

    def __init__(
            self,
            x: int,
            y: int,
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface
    ) -> None:
        tile: dict = game_data.tiles["TRAP"]

        super().__init__(
            x,
            y,
            tile["Name"],
            tile["Desc"],
            tile["Blocked"],
            tile["Character"],
            tile["Color"],
            game_data,
            game_entities_,
            game_interface,
            tile["Cover Percent"],
            False
        )

        self.triggered: bool = False

        self.game_entities.traps.append(self)

    def trigger(self) -> None:
        """Triggers the trap and performs some action."""

        if self.triggered:
            return

        # Later implement different nasty effects such as shocking the player.
        self.triggered = True
        self.visible = True


class Explosive(Entity):
    """Represents an explosive on the map before and after it goes off."""

    def __init__(
            self,
            x: int,
            y: int,
            damage: int,
            blast_radius: int,
            fuse: int,
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface
    ) -> None:
        tile: dict = game_data.tiles["EXPLOSIVE"]

        super().__init__(
            x,
            y,
            tile["Name"],
            tile["Desc"],
            tile["Blocked"],
            tile["Character"],
            tile["Color"],
            game_data,
            game_entities_,
            game_interface
        )

        self.fuse = fuse  # How many rounds before going off.
        self.damage = damage
        self.blast_radius = blast_radius

        game_entities_.explosives.append(self)

    def explode(self) -> None:
        """Called after the fuse has run out and unleashes an explosion."""

        actors_hit: list[Actor] = []  # Used to keep track of actors receiving damage so they don't get hit twice.

        # Grows the explosion out to its max blast radius.
        for i in range(self.blast_radius + 1):
            blast_zone: list[tuple[int, int]]
            if i == 0:
                # The explosion is directly under an actor.
                blast_zone = [(self.x, self.y)]
            else:
                blast_zone = self.compute_fov(i, False)

            # Check each point in the blast zone to see if it hit an actor.
            for point in blast_zone:
                actor: Actor = self.game_entities.get_actor_at(point[0], point[1])
                if actor is not None and actor.health >= 0 and actor not in actors_hit:
                    actor.receive_hit(self, round(self.damage / (i + 1)), 100)
                    actors_hit.append(actor)

            self.render_projectile(blast_zone, '*', self.game_data.colors["RED"], 0.05)

        self.remove()

    def update(self, game_time: int) -> None:
        """Updates the explosive."""

        # Decrease the fuse every round.
        self.fuse -= 1
        if self.fuse <= 0:
            self.explode()

    def remove(self) -> None:
        """Removes the explosive from the list of all explosives."""

        explosives: list[Explosive] = self.game_entities.explosives
        for explosive_ in enumerate(explosives):
            if explosive_[1] is self:
                explosives.pop(explosive_[0])

        super().remove()
