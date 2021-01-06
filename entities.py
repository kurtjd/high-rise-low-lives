import math
import time
from enum import Enum, auto
from typing import Optional, Callable, Any
import tcod
import databases
import interface
import items
import ai


class GameEntities:
    def __init__(self, window: tcod.context.Context, console: tcod.Console) -> None:
        self.all: list[Entity] = []
        self.tiles: list[Tile] = []
        self.actors:  list[Actor] = []
        self.turrets: list[Turret] = []
        self.doors:  list[Door] = []
        self.items:  list[ItemEntity] = []
        self.terminals:  list[Terminal] = []
        self.cameras:  list[Camera] = []
        self.traps: list[Trap] = []
        self.vents: list[Vent] = []
        self.explosives: list[Explosive] = []
        self.player: Optional[Player] = None

        self.window = window
        self.console = console

    def get_all_at(self, x: int, y: int) -> list["Entity"]:
        return [entity_ for entity_ in self.all if entity_.x == x and entity_.y == y]

    def get_actor_at(self, x: int, y: int) -> Optional["Actor"]:
        for actor_ in self.actors:
            if actor_.x == x and actor_.y == y:
                return actor_
        return None

    def get_door_at(self, x: int, y: int) -> Optional["Door"]:
        for door_ in self.doors:
            if door_.x == x and door_.y == y:
                return door_
        return None

    def get_items_at(self, x: int, y: int) -> list["ItemEntity"]:
        return [item_ for item_ in self.items if item_.x == x and item_.y == y]

    def get_terminal_at(self, x: int, y: int) -> Optional["Terminal"]:
        for terminal_ in self.terminals:
            if terminal_.x == x and terminal_.y == y:
                return terminal_
        return None

    def get_trap_at(self, x: int, y: int) -> Optional["Trap"]:
        for trap_ in self.traps:
            if trap_.x == x and trap_.y == y:
                return trap_
        return None

    def get_vent_at(self, x: int, y: int) -> Optional["Vent"]:
        for vent_ in self.vents:
            if vent_.x == x and vent_.y == y:
                return vent_
        return None

    # Draws all game entities to the screen.
    def render_all(self, console: tcod.Console) -> None:
        for tile_ in self.tiles:
            tile_.render(console)

        for vent_ in self.vents:
            vent_.render(console)

        for camera_ in self.cameras:
            camera_.render(console)

        for trap_ in self.traps:
            trap_.render(console)

        for item_ in self.items:
            item_.render(console)

        for door_ in self.doors:
            door_.render(console)

        for terminal_ in self.terminals:
            terminal_.render(console)

        for turret_ in self.turrets:
            turret_.render(console)

        for explosive_ in self.explosives:
            explosive_.render(console)

        for actor_ in self.actors:
            actor_.render(console)

    # Called every tick of time to update entities.
    def update_all(self, game_time: int) -> None:
        for entity_ in self.all:
            entity_.update(game_time)

    # Clears and resets all the lists.
    def reset(self) -> None:
        self.all = []
        self.actors = []
        self.doors = []
        self.items = []

    # Reveals the vents and hides everything else.
    def show_vents(self):
        for entity in self.all:
            if isinstance(entity, Vent) or isinstance(entity, Player):
                entity.visible = True
            else:
                entity.old_visible = entity.visible
                entity.visible = False

    def hide_vents(self):
        for entity in self.all:
            if isinstance(entity, Vent) and not entity.entrance:
                entity.visible = False
            else:
                entity.visible = entity.old_visible


class Entity:
    # ~~~ STATIC METHODS ~~~

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
        self.graphic: str = graphic
        self.color: Optional[tuple[int, int, int]] = color
        self.bgcolor: Optional[tuple[int, int, int]] = None
        self.blocked: bool = blocked
        self.old_visible: bool = visible  # Used to keep track of visibility before player ents vents
        self.visible: bool = visible
        self.game_data: databases.Databases = game_data
        self.game_interface: interface.Interface = game_interface
        self.game_entities: GameEntities = game_entities_

        self.noise_level: int = 0
        self.cover_percent = cover_percent

        game_entities_.all.append(self)

    # ~~~ PUBLIC METHODS ~~~

    # Draws a game entity to the screen
    def render(self, console: tcod.Console) -> None:
        if self.visible:
            console.print(x=self.x, y=self.y, string=self.graphic, fg=self.color, bg=self.bgcolor)

    def update(self, game_time: int) -> None:
        pass

    def remove(self) -> None:
        for entity_ in enumerate(self.game_entities.all):
            if entity_[1] is self:
                self.game_entities.all.pop(entity_[0])

    def make_noise(self, noise_radius: int) -> None:
        self.noise_level = noise_radius

    # Uses the bresenham line algorithm to get a list of points on the map the LOS would pass through.
    def get_line_of_sight(
            self,
            x2: int,
            y2: int,
            extend: bool = False,
            ignore_cover: bool = True
    ) -> list[tuple[int, int]]:
        end_x: int = x2
        end_y: int = y2

        # Extend the path beyond where entity selected using slope of line.
        if extend:
            end_x = x2 + ((x2 - self.x) * 20)
            end_y = y2 + ((y2 - self.y) * 20)

        # Disclude the entity from the LOS.
        los: list[tuple[int, int]] = tcod.los.bresenham((self.x, self.y), (end_x, end_y)).tolist()[1:]

        # Check each point in the LOS if it's 100% cover (basically meaning it's a wall). If so, stop the LOS there.
        final_los: list[tuple[int, int]] = []
        for point in los:
            final_los.append(point)
            for entity in self.game_entities.get_all_at(point[0], point[1]):
                if entity.cover_percent == 100 or (not ignore_cover and entity.blocked):
                    return final_los

        return final_los

    def render_sleep(
            self,
            points: list[tuple[int, int]],
            char: str,
            color: tuple[int, int, int],
            delay: float
    ) -> None:
        self.game_entities.render_all(self.game_entities.console)
        for point in points:
            self.game_entities.console.print(
                x=point[0],
                y=point[1],
                string=char,
                fg=color
            )
        self.game_entities.window.present(self.game_entities.console)
        time.sleep(delay)

    def compute_fov(self, radius: int, ignore_cover: bool = True) -> list[tuple[int, int]]:
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

    # Actors can be performing one of these actions:
    class Actions(Enum):
        NONE: int = auto(),
        MOVE: int = auto(),
        ATK_MELEE: int = auto(),
        ATK_RANGED: int = auto(),
        WIELD: int = auto(),
        OPEN_DOOR: int = auto(),
        CLOSE_DOOR: int = auto(),
        REST: int = auto(),
        PICKUP: int = auto(),
        HACK: int = auto(),
        THROW: int = auto(),
        USE_DRUG: int = auto(),
        CHARGE: int = auto()

    # ~~~ PRIVATE METHODS ~~~

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
            is_player: bool,
            graphic: str,
            color: tuple[int, int, int],
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface
    ) -> None:
        super().__init__(x, y, name, desc, True, graphic, color, game_data, game_entities_, game_interface)

        # Descriptors
        self.race: str = race
        self.class_name: str = class_name
        self.is_player: bool = is_player

        # This contains a function name corresponding to one of the AI functions in ai.py
        self.ai: Callable[[Actor, list[Actor]], None] = ai_

        # Attributes
        self.health: int = health
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
        self.mp: int = 50
        self.ac: int = 6
        self.base_atk_dmg: int = 10
        self.atk_dmg: int = self.base_atk_dmg
        self.gen_speed: int = 5
        self.move_speed: int = 10
        self.atk_speed: int = 10
        self.wield_speed: int = 5
        self.hack_speed: int = 20
        self.rest_speed: int = 10
        self.throw_speed = 8
        self.recovery_rate: int = 10

        # Inventory/Equipped
        self.MAX_INVENTORY_SIZE: int = 52
        self.inventory: dict = {}
        self.wielding: Optional[str] = None
        self.wearing: Optional[str] = None
        self.throwing: Optional[items.Item] = None

        # These properties are used to track actions.
        self.action_target: Any = None  # Used when the target isn't an x/y
        self.action_delay: int = -1
        self.action_target_x: int = 0
        self.action_target_y: int = 0
        self.action: int = Actor.Actions.NONE
        self.dest_x: int = 0
        self.dest_y: int = 0
        self.atk_target: Optional[Entity] = None
        self.bullet_path: list[tuple[int, int]] = []

        # Misc
        self.in_vents: bool = False

        # If not the player, set a default action. For now, just rest.
        if not is_player:
            self._set_action(self.Actions.REST, 1)

        game_entities_.actors.append(self)

    # ~~~ UTILITY METHODS ~~~
    # Let the AI think of a new action.
    def _think(self) -> None:
        # This uses the function name stored in self.ai to call one of the AI functions and passes self
        self.ai(self, self.game_entities.actors)

    # Finds the correct a-zA-Z character to assign as an id to a newly acquired items.
    def _get_next_item_id(self) -> str:
        # Item IDs can be a-zA-Z so loop through all ASCII numbers skipping the non-alpha in between.
        for item_id in range(65, 123):
            if 91 <= item_id <= 96:
                continue

            if not chr(item_id) in self.inventory:
                return chr(item_id)

    # Decreases the amount of an item in the inventory and deletes it if zero.
    def _dec_item_count(self, item_id: str, amount: int = 1):
        self.inventory[item_id]["Amount"] -= amount

        if self.inventory[item_id]["Amount"] == 0:
            del self.inventory[item_id]

    # Actors can potentially be reanimated so it is only "playing" dead
    def _play_dead(self) -> None:
        self.graphic = self.game_data.tiles["CORPSE"]["Character"]
        self.color = self.game_data.tiles["CORPSE"]["Color"]
        self.blocked = self.game_data.tiles["CORPSE"]["Blocked"]

        # Just quit the game for now to prevent crash.
        if self.is_player:
            raise SystemExit()

    # Recovers stats
    def _recover(self) -> None:
        self.health += 1
        if self.health > 100:
            self.health = 100

    # Queues an action and sets the delay and target of the action.
    def _set_action(
            self,
            action: int,
            delay: int,
            target_x: int = 0,
            target_y: int = 0
    ) -> None:
        self.action = action
        self.action_delay = delay
        self.action_target_x = target_x
        self.action_target_y = target_y

    # Called after action is performed. Resets all counters and associated variables.
    def _reset_action(self) -> None:
        self.action = self.Actions.NONE
        self.action_target_x = 0
        self.action_target_y = 0
        self.action_delay = -1  # -1 represents no action queued
        self.dest_x = 0
        self.dest_y = 0

        # Allow the AI to think of a new action.
        if not self.is_player:
            self._think()

    # Actually performs the action by calling the appropriate method.
    def _do_action(self) -> None:
        if self.action == self.Actions.ATK_MELEE:
            self._attack_melee()
        elif self.action == self.Actions.ATK_RANGED:
            self._attack_ranged()
        elif self.action == self.Actions.MOVE:
            self.move()
        elif self.action == self.Actions.OPEN_DOOR:
            self._open_door()
        elif self.action == self.Actions.CLOSE_DOOR:
            self._close_door()
        elif self.action == self.Actions.REST:
            self._rest()
        elif self.action == self.Actions.PICKUP:
            self._pick_up()
        elif self.action == self.Actions.WIELD:
            self._wield()
        elif self.action == self.Actions.HACK:
            self._hack()
        elif self.action == self.Actions.THROW:
            self._throw()
        elif self.action == self.Actions.USE_DRUG:
            self._use_drug()
        elif self.action == self.Actions.CHARGE:
            self._charge()

    # Attempts to open a door.
    def _open_door(self) -> None:
        target_door: Door = self.game_entities.get_door_at(self.action_target_x, self.action_target_y)
        if not target_door.locked:
            target_door.open()
        else:
            self.game_interface.message_box.add_msg(
                f"That door is locked.", self.game_data.colors["ERROR_MSG"]
            )

    # Attempts to hack a terminal.
    def _hack(self) -> None:
        target_terminal: Terminal = self.game_entities.get_terminal_at(
            self.action_target_x,
            self.action_target_y
        )
        target_terminal.attempt_hack(self)

    # Performs a melee attack
    def _attack_melee(self) -> None:
        target_actor: Actor = self.game_entities.get_actor_at(self.action_target_x, self.action_target_y)
        # The Actor, if fast enough, may have moved away before attack could finish
        # Or player purposely attempts to attack something that can't be attacked
        if target_actor is None:
            self.game_interface.message_box.add_msg(
                f"{self.name} attacks thin air!", self.game_data.colors["ERROR_MSG"]
            )
            return

        # Don't attack dead Actors
        if target_actor.health <= 0:
            return

        target_actor.receive_hit(self, self.atk_dmg, 100)

    # Performs a ranged attack
    def _attack_ranged(self) -> None:
        # Check each point within the bullet path for something that can be attacked.
        prev_entity_cover: int = 0
        for point in self.bullet_path:
            entity_at_point: Entity = self.game_entities.get_all_at(point[0], point[1])[-1]
            if isinstance(entity_at_point, Actor) and entity_at_point.health > 0:
                entity_at_point.receive_hit(self, self.atk_dmg, 100 - prev_entity_cover, True)
                return
            else:
                prev_entity_cover = entity_at_point.cover_percent

            self.render_sleep([(point[0], point[1])], ')', tcod.red, 0.01)

        self.game_interface.message_box.add_msg(
            f"{self.name} shoots at nothing.", self.game_data.colors["ERROR_MSG"]
        )

    def _throw(self) -> None:
        # Draw the throwable as it goes through the air
        for point in self.bullet_path:
            self.render_sleep([(point[0], point[1])], ')', tcod.red, 0.01)

        x: int
        y: int

        # If the player dropped a grenade at their feet:
        if not self.bullet_path:
            x = self.x
            y = self.y
        else:
            entity_at_end: Entity = self.game_entities.get_all_at(self.bullet_path[-1][0], self.bullet_path[-1][1])[-1]

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

    # Update what the player is wielding and change stats to reflect that.
    def _wield(self) -> None:
        if self.action_target is None:
            self.wielding = None
            self.atk_dmg = self.base_atk_dmg
            self.game_interface.message_box.add_msg(
                f"{self.name} readies his fists.", self.game_data.colors["SUCCESS_MSG"]
            )
        else:
            self.wielding = self.action_target.name
            self.atk_dmg = self.base_atk_dmg + self.action_target.dmg
            self.game_interface.message_box.add_msg(
                f"{self.name} wields a {self.action_target.name}.", self.game_data.colors["SUCCESS_MSG"]
            )

    def _use_drug(self):
        drug: items.Drug = self.inventory[self.action_target]["Item"]
        drug.effect(self)

        self.game_interface.message_box.add_msg(
            f"{self.name} uses {drug.name}", self.game_data.colors["SUCCESS_MSG"]
        )

        self._dec_item_count(self.action_target)

    def _charge(self):
        powersrc: items.PowerSource = self.inventory[self.action_target]["Item"]
        self.charge_percent += powersrc.charge_held

        self.game_interface.message_box.add_msg(
            f"{self.name} receives {powersrc.charge_held}% charge from a {powersrc.name}.",
            self.game_data.colors["SUCCESS_MSG"]
        )

        self._dec_item_count(self.action_target)

    # Actually closes the door.
    def _close_door(self) -> None:
        target_door: Door = self.game_entities.get_door_at(self.action_target_x, self.action_target_y)
        target_door.close()

    # Actually rests
    # Essentially does nothing.
    def _rest(self) -> None:
        pass

    # Actually picks up an items.
    def _pick_up(self) -> None:
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

    # ~~~ PUBLIC METHODS ~~~

    # Adds an item to the inventory
    def add_inventory(self, item_: items.Item, amount: int = 1) -> None:
        self.inventory[self._get_next_item_id()] = {"Item": item_, "Amount": amount}

    # Called by anything that wants to damage this actor.
    def receive_hit(self, src_entity: Entity, atk_dmg: int, hit_chance: int, ranged: bool = False) -> None:
        # Calculate random and shit later
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
                        f"{src_entity.wielding} for {atk_dmg} damage!"
                    )
                else:
                    hit_msg = f"{src_entity.name} hits {self.name} with his {src_entity.wielding} for {atk_dmg} damage!"
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

            self._play_dead()

        self.game_interface.message_box.add_msg(hit_msg, msg_color)

    # ~~~ ACTION METHODS ~~~
    # Moves to a new position.
    def move(self) -> None:
        # We need to check again that the destination isn't blocked in case something moved there in the meantime.
        for dest_entity in self.game_entities.get_all_at(self.dest_x, self.dest_y):
            if dest_entity.blocked:
                if self.is_player:
                    self.game_interface.message_box.add_msg(
                        f"{self.name} slams into something.", self.game_data.colors["ERROR_MSG"]
                    )
                return

        self.x = self.dest_x
        self.y = self.dest_y

    def get_wieldable_items(self) -> [items.Item]:
        return [item_ for item_ in self.inventory.items() if item_[1]["Item"].wieldable]

    def get_throwable_items(self) -> [items.Item]:
        return [item_ for item_ in self.inventory.items() if item_[1]["Item"].throwable]

    def get_drug_items(self) -> [items.Drug]:
        return [item_ for item_ in self.inventory.items() if isinstance(item_[1]["Item"], items.Drug)]

    def get_power_sources(self) -> [items.PowerSource]:
        return [item_ for item_ in self.inventory.items() if isinstance(item_[1]["Item"], items.PowerSource)]

    # Calls the appropriate attack function.
    def attempt_atk(
            self,
            x: int,
            y: int,
            ranged: bool = False,
            bullet_path: Optional[list[tuple[int, int]]] = None
    ) -> None:
        if not ranged:
            self._set_action(self.Actions.ATK_MELEE, self.atk_speed, x, y)
        else:
            self.bullet_path = bullet_path
            self._set_action(self.Actions.ATK_RANGED, self.atk_speed, x, y)

    # Makes sure the Actor can actually move to where it wants to go.
    def attempt_move(self, x: int, y: int) -> bool:
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
                    self._set_action(self.Actions.OPEN_DOOR, self.gen_speed, new_x, new_y)
                    return True
                elif isinstance(dest_entity, Terminal):
                    self._set_action(self.Actions.HACK, self.hack_speed, new_x, new_y)
                    return True
                elif isinstance(dest_entity, Vent) and not self.is_player:
                    return False  # Don't let NPCs follow player into vents

                # Prevent from moving into blocked entity.
                elif dest_entity.blocked:
                    return False

        # If destination is not blocked and is not a living Actor, move to it
        self._set_action(self.Actions.MOVE, self.move_speed)
        return True

    def attempt_throw(self, x: int, y: int, item: items.Item, throw_path: Optional[list[tuple[int, int]]] = None):
        self.bullet_path = throw_path
        self.throwing = item
        self._set_action(self.Actions.THROW, self.throw_speed, x, y)

    # Attempts to pick an item up off the floor where the Actor is standing.
    def attempt_pickup(self) -> None:
        # Only pick up if there's something on the floor.
        if self.game_entities.get_items_at(self.x, self.y):
            self._set_action(self.Actions.PICKUP, self.gen_speed, self.x, self.y)
        elif self.is_player:
            self.game_interface.message_box.add_msg(
                "There's nothing here to pickup.", self.game_data.colors["ERROR_MSG"]
            )

    # Attempts to wield a new weapon
    def attempt_wield(self, new_weapon: Optional[items.Item]) -> None:
        # Make sure attempting to wield an actual weapon.
        # Include None because that is fists.
        if (new_weapon is not None and not isinstance(new_weapon, items.Weapon)) and self.is_player:
            self.game_interface.message_box.add_msg(
                f"{self.name} cannot wield a {new_weapon.name}.", self.game_data.colors["ERROR_MSG"]
            )
            return

        # Finally set the action and send a message.
        self.action_target = new_weapon
        self._set_action(self.Actions.WIELD, self.wield_speed)

    def attempt_use_drug(self, drug_id: str):
        self.action_target = drug_id
        self._set_action(self.Actions.USE_DRUG, self.gen_speed)

    def attempt_charge(self, powersrc_id: str):
        self.action_target = powersrc_id
        self._set_action(self.Actions.CHARGE, self.gen_speed)

    # Checks for open doors around the Actor and closes them if they exist.
    def attempt_close_door(self) -> None:
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x != 0 or y != 0:
                    target_door: Door = self.game_entities.get_door_at(self.x + x, self.y + y)
                    if target_door is not None and target_door.opened:
                        self._set_action(self.Actions.CLOSE_DOOR, self.gen_speed, target_door.x, target_door.y)
                        return

        if self.is_player:
            self.game_interface.message_box.add_msg(
                "There's no door to be closed here.", self.game_data.colors["ERROR_MSG"]
            )

    # Actor rests to recover HP and other stuff
    def attempt_rest(self) -> None:
        self._set_action(self.Actions.REST, self.rest_speed)

    # Called every tick of game time.
    def update(self, game_time: int) -> None:
        # Do nothing if dead.
        if self.health <= 0:
            return

        # Check if time to recover
        if game_time > 0 and (game_time % self.recovery_rate) == 0:
            self._recover()

        # Only delay action if the actor has an action queued
        if self.action_delay > 0:
            self.action_delay -= 1

            # Perform the action and think of a new one.
            if self.action_delay == 0:
                self._do_action()
                self._reset_action()


# This is a small class since the player mostly shares characteristics with other actors except a few things.
class Player(Actor):
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
                         None, True, graphic, color, game_data, game_entities_, game_interface)

        self.examine_target: Any = None
        self.item_selected: Optional[items.Item] = None

        self.max_charge_loss_delay: int = 100  # The number of turns before losing a percent of charge.
        self.charge_loss_delay = self.max_charge_loss_delay

        game_entities_.player = self

    def move(self) -> None:
        super().move()

        # If the player moves into or out of vents, change what is visible.
        vent: Vent = self.game_entities.get_vent_at(self.x, self.y)
        if vent is not None:
            if not self.in_vents:
                self.game_entities.show_vents()
                self.in_vents = True
                self.move_speed = self.move_speed * 2  # Makes moving slower in vents
            elif vent.entrance:
                self.game_entities.hide_vents()
                self.in_vents = False
                self.move_speed = self.move_speed / 2  # Return to normal speed.
        elif self.in_vents:
            self.game_entities.hide_vents()
            self.in_vents = False
            self.move_speed = self.move_speed / 2  # Return to normal speed.

        # If the player walks onto a trap, trigger it.
        trap: Trap = self.game_entities.get_trap_at(self.x, self.y)
        if trap is not None:
            trap.trigger()

    def attempt_move(self, x: int, y: int) -> bool:
        # The destination the player is attempting to move to
        new_x: int = self.x + x
        new_y: int = self.y + y

        # If the player is in the vents, make it so they can't move through un-blocked entities like floors.
        vent_to: Vent = self.game_entities.get_vent_at(new_x, new_y)
        vent_on: Vent = self.game_entities.get_vent_at(self.x, self.y)

        if self.in_vents and vent_to is None and vent_on is not None and not vent_on.entrance:
            return False

        if not self.in_vents and\
                ((vent_to is not None and not vent_to.entrance) and (vent_on is None or not vent_on.entrance)):
            return False

        super().attempt_move(x, y)

    def update(self, game_time: int) -> None:
        super().update(game_time)
        self.charge_loss_delay -= 1

        if self.charge_loss_delay == 0:
            self.charge_percent -= 1
            self.charge_loss_delay = self.max_charge_loss_delay


class Turret(Actor):
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
            False,
            self.turret_data["Graphic"],
            self.turret_data["Color"],
            game_data,
            game_entities_,
            game_interface
        )

        self.game_entities.turrets.append(self)


class ItemEntity(Entity):
    # ~~~ PRIVATE METHODS ~~~

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
        self.item: items.Item = item_
        game_entities_.items.append(self)

    # ~~~ PUBLIC METHODS ~~~

    def actor_pick_up(self, actor_: Actor) -> items.Item:
        actor_.add_inventory(self.item, 1)
        self.remove()

        return self.item

    def remove(self) -> None:
        game_items: list[ItemEntity] = self.game_entities.items
        for item_ in enumerate(game_items):
            if item_[1] is self:
                game_items.pop(item_[0])

        super().remove()


# Represents static map tiles like floors and walls.
class Tile(Entity):
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
    def __init__(
            self,
            x: int,
            y: int,
            game_data: databases.Databases,
            game_entities_: GameEntities,
            game_interface: interface.Interface,
            entrance: bool = False
    ) -> None:
        self.entrance: bool = entrance
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
    # ~~~ PRIVATE METHODS ~~~

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

    # ~~~ PUBLIC METHODS ~~~

    # Changes the appearance of the door and makes it no longer blocked.
    def open(self) -> None:
        self.opened = True
        self.blocked = False
        self.graphic = self.game_data.tiles["DOOR_OPEN"]["Character"]
        self.color = self.game_data.tiles["DOOR_OPEN"]["Color"]
        self.cover_percent = self.game_data.tiles["DOOR_OPEN"]["Cover Percent"]

    def close(self) -> None:
        self.opened = False
        self.blocked = True
        self.graphic = self.game_data.tiles["DOOR_CLOSED"]["Character"]
        self.color = self.game_data.tiles["DOOR_CLOSED"]["Color"]
        self.cover_percent = self.game_data.tiles["DOOR_CLOSED"]["Cover Percent"]


# Terminals can be hacked to do things like:
# open doors, turn off security cameras, disable turrets and traps, download programs, etc
# If failed to hack, can do nasty things like sound an alarm, explode, give you a virus, etc
class Terminal(Entity):
    class SuccessResult(Enum):
        DISABLE_CAMS: int = auto(),
        DISABLE_TURRETS: int = auto(),
        UNLOCK_DOORS: int = auto()

    class FailResult(Enum):
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

    # This will decide randomly which and how many success/fail results to generate for this terminal.
    # The number of success will increase difficulty and the higher the difficulty the more number of fails.
    def _choose_results(self) -> None:
        self.success_results.append(self.SuccessResult.UNLOCK_DOORS)
        self.fail_results.append(self.FailResult.SOUND_ALARM)
        self.difficulty = 5

    def _unlock_doors(self) -> None:
        for door in self.game_entities.doors:
            door.locked = False

        self.game_interface.message_box.add_msg(
            f"All doors unlocked.", self.game_data.colors["SYS_MSG"]
        )

    def _sound_alarm(self) -> None:
        self.make_noise(50)
        self.game_interface.message_box.add_msg(
            f"Alarms sounded.", self.game_data.colors["SYS_MSG"]
        )

    # What happens when successfully hacked.
    def _success_hack(self, actor_: Actor) -> None:
        self.game_interface.message_box.add_msg(
            f"{actor_.name} successfully hacks the terminal.", self.game_data.colors["SUCCESS_MSG"]
        )

        for result in self.success_results:
            if result == self.SuccessResult.UNLOCK_DOORS:
                self._unlock_doors()

    # What happens when unsuccessfully hacked.
    def _fail_hack(self, actor_: Actor) -> None:
        self.game_interface.message_box.add_msg(
            f"{actor_.name} fails to hack the terminal.", self.game_data.colors["BAD_MSG"]
        )

        for result in self.fail_results:
            if result == self.FailResult.SOUND_ALARM:
                self._sound_alarm()

    # Called by an actor that wants to attempt to hack the terminal.
    def attempt_hack(self, actor_: Actor) -> None:
        if actor_.hacking_skill > self.difficulty:
            self._success_hack(actor_)
        else:
            self._fail_hack(actor_)


class Camera(Entity):
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
        if not self.triggered:
            # Check if player is within FOV, if so sound alarms.
            # Eventually also do stealth check.
            for point in self.fov:
                if point[0] == self.game_entities.player.x and point[1] == self.game_entities.player.y:
                    self.triggered = True
                    self.game_interface.message_box.add_msg(
                        f"You've been spotted! Alarms sounded!", self.game_data.colors["SYS_MSG"]
                    )
                    break

        if self.triggered:
            self.make_noise(50)


class Trap(Entity):
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
        if self.triggered:
            return

        # Later implement different nasty effects such as shocking the player.
        print("Trap triggered!")
        self.triggered = True
        self.visible = True


class Explosive(Entity):
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
        actors_hit: list[Actor] = []

        for i in range(self.blast_radius + 1):
            blast_zone: list[tuple[int, int]]
            if i == 0:
                blast_zone = [(self.x, self.y)]
            else:
                blast_zone = self.compute_fov(i, False)

            for point in blast_zone:
                actor: Actor = self.game_entities.get_actor_at(point[0], point[1])
                if actor is not None and actor.health >= 0 and actor not in actors_hit:
                    actor.receive_hit(self, round(self.damage / (i + 1)), 100)
                    actors_hit.append(actor)

            self.render_sleep(blast_zone, '*', tcod.red, 0.05)

        self.remove()

    def update(self, game_time: int) -> None:
        self.fuse -= 1
        if self.fuse <= 0:
            self.explode()

    def remove(self) -> None:
        explosives: list[Explosive] = self.game_entities.explosives
        for explosive_ in enumerate(explosives):
            if explosive_[1] is self:
                explosives.pop(explosive_[0])

        super().remove()
