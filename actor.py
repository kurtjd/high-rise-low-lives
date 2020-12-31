from collections.abc import Callable
from enum import Enum, auto
from typing import Optional, Any
import game_entities
import databases
import interface
import entity
import weapon
import door
import terminal
import item_entity
import item


class Actor(entity.Entity):

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
        HACK: int = auto()

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
            ai: Optional[Callable[..., None]],
            is_player: bool,
            graphic: str,
            color: tuple[int, int, int],
            game_data: databases.Databases,
            game_entities_: "game_entities.GameEntities",
            game_interface: interface.Interface
    ) -> None:
        super().__init__(x, y, name, desc, True, graphic, color, game_entities_)

        # Descriptors
        self.race: str = race
        self.class_name: str = class_name
        self.is_player: bool = is_player

        # This contains a function name corresponding to one of the AI functions in ai.py
        self.ai: Callable[[Actor, list[Actor]], None] = ai

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
        self.mp: int = 50
        self.charge: int = 100
        self.ac: int = 6
        self.base_atk_dmg: int = 10
        self.atk_dmg: int = self.base_atk_dmg
        self.gen_speed: int = 5
        self.move_speed: int = 10
        self.atk_speed: int = 10
        self.wield_speed: int = 5
        self.hack_speed: int = 20
        self.rest_speed: int = 10
        self.recovery_rate: int = 10

        # Inventory/Equipped
        self.MAX_INVENTORY_SIZE: int = 52
        self.inventory: list[dict] = []
        self.wielding: Optional[str] = None
        self.wearing: Optional[str] = None

        # These properties are used to track actions.
        self.action_target: Any = None  # Used when the target isn't an x/y
        self.action_delay: int = -1
        self.action_target_x: int = 0
        self.action_target_y: int = 0
        self.action: int = Actor.Actions.NONE
        self.dest_x: int = 0
        self.dest_y: int = 0
        self.atk_target: Optional[entity.Entity] = None
        self.bullet_path: list[tuple[int, int]] = []

        # Misc
        self.game_data: databases.Databases = game_data
        self.game_interface: interface.Interface = game_interface

        # If not the player, set a default action. For now, just rest.
        if not is_player:
            self._set_action(self.Actions.REST, 0)

        game_entities_.actors.append(self)

    # ~~~ UTILITY METHODS ~~~
    # Let the AI think of a new action.
    def _think(self) -> None:
        # This uses the function name stored in self.ai to call one of the AI functions and passes self
        self.ai(self, self.game_entities.actors)

    # Finds the correct a-zA-Z character to assign as an id to a newly acquired item.
    def _get_next_item_id(self) -> str:
        # Item IDs can be a-zA-Z so loop through all ASCII numbers skipping the non-alpha in between.
        for item_id in range(65, 123):
            if 91 <= item_id <= 96:
                continue

            # For each potential item id, check if an existing item already has that id. If not, then assign as new id.
            empty_id: bool = True
            for exist_item in self.inventory:
                if exist_item["ID"] == chr(item_id):
                    empty_id = False
                    break
            if empty_id:
                return chr(item_id)

    # Actors can potentially be reanimated so it is only "playing" dead
    def _play_dead(self) -> None:
        self.graphic = self.game_data.tiles["CORPSE"]["Character"]
        self.color = self.game_data.tiles["CORPSE"]["Color"]
        self.blocked = self.game_data.tiles["CORPSE"]["Blocked"]

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
            self._move()
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

    # ~~~ ACTION METHODS ~~~
    # Moves to a new position.
    def _move(self) -> None:
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

    # Attempts to open a door.
    def _open_door(self) -> None:
        target_door: door.Door = self.game_entities.get_door_at(self.action_target_x, self.action_target_y)
        if not target_door.locked:
            target_door.open()
        else:
            self.game_interface.message_box.add_msg(
                f"That door is locked.", self.game_data.colors["ERROR_MSG"]
            )

    # Attempts to hack a terminal.
    def _hack(self) -> None:
        target_terminal: terminal.Terminal = self.game_entities.get_terminal_at(
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

        # Hurt the target.
        target_actor.take_damage(self.atk_dmg)

        # Send different message depending on what is attacked with.
        # Change color depending on if player or not.
        msg_color: [int]
        if self.is_player:
            msg_color = self.game_data.colors["ATK_MSG"]
        else:
            msg_color = self.game_data.colors["BAD_MSG"]

        if target_actor.health > 0:
            if self.wielding is None:
                self.game_interface.message_box.add_msg(
                    f"{self.name} pummels {target_actor.name} with his fists for {self.atk_dmg} dmg!",
                    msg_color
                )
            else:
                self.game_interface.message_box.add_msg(
                    f"{self.name} hits {target_actor.name} with his {self.wielding} for {self.atk_dmg} dmg!",
                    msg_color
                )
        else:
            self.game_interface.message_box.add_msg(
                f"{self.name} guts {target_actor.name}.", self.game_data.colors["KILL_MSG"]
            )

    # Performs a ranged attack
    def _attack_ranged(self) -> None:
        # Check each point within the bullet path for something that can be attacked.
        for point in self.bullet_path:
            target_actor: Actor = self.game_entities.get_actor_at(point[0], point[1])
            # The Actor, if fast enough, may have moved away before attack could finish
            # Or player purposely attempts to attack something that can't be attacked
            if target_actor is None or target_actor.health <= 0:
                continue

            # Hurt the target.
            target_actor.take_damage(self.atk_dmg)

            # Send different message depending on what is attacked with.
            # Change color depending on if player or not.
            msg_color: [int]
            if self.is_player:
                msg_color = self.game_data.colors["ATK_MSG"]
            else:
                msg_color = self.game_data.colors["BAD_MSG"]

            if target_actor.health > 0:
                self.game_interface.message_box.add_msg(
                    f"{self.name} shoots {target_actor.name} with his {self.wielding} for {self.atk_dmg} dmg!",
                    msg_color
                )
            else:
                self.game_interface.message_box.add_msg(
                    f"{self.name} executes {target_actor.name}.", self.game_data.colors["KILL_MSG"]
                )

            return

        self.game_interface.message_box.add_msg(
            f"{self.name} shoots at nothing.", self.game_data.colors["ERROR_MSG"]
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

    # Actually closes the door.
    def _close_door(self) -> None:
        target_door: door.Door = self.game_entities.get_door_at(self.action_target_x, self.action_target_y)
        target_door.close()

    # Actually rests
    # Essentially does nothing.
    def _rest(self) -> None:
        pass

    # Actually picks up an item.
    def _pick_up(self) -> None:
        # Get all items at target and ask which to pick-up
        # For now just pick up first item
        items: list[item_entity.ItemEntity] = self.game_entities.get_items_at(
            self.action_target_x,
            self.action_target_y
        )
        item_ = items[0].actor_pick_up(self)

        self.game_interface.message_box.add_msg(
            f"{self.name} picks up a {item_.name}.", self.game_data.colors["SUCCESS_MSG"]
        )

    # ~~~ PUBLIC METHODS ~~~

    # Adds an item to the inventory
    def add_inventory(self, item_: item.Item, amount: int = 1) -> None:
        self.inventory.append(dict({"ID": self._get_next_item_id(), "Item": item_, "Amount": amount}))

    # Called by anything that wants to damage this actor.
    def take_damage(self, amount: int) -> None:
        self.health -= amount
        if self.health <= 0:
            self._play_dead()

    # Returns a list of wieldable items from actors inventory.
    def get_wieldable_items(self) -> [weapon.Weapon]:
        return [item_ for item_ in self.inventory if isinstance(item_["Item"], weapon.Weapon)]

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
    def attempt_move(self, x: int, y: int) -> None:
        # The destination the actor is attempting to move to
        new_x: int = self.x + x
        new_y: int = self.y + y

        # We want to check what entites are occupying the move destination
        dest_entities: list[entity.Entity] = self.game_entities.get_all_at(new_x, new_y)
        for dest_entity in dest_entities:
            # Check to see if destination has an Actor, if so perform melee attack
            if isinstance(dest_entity, Actor):
                self.attempt_atk(new_x, new_y)
            elif isinstance(dest_entity, door.Door) and not dest_entity.opened:
                self._set_action(self.Actions.OPEN_DOOR, self.gen_speed, new_x, new_y)
            elif isinstance(dest_entity, terminal.Terminal):
                self._set_action(self.Actions.HACK, self.hack_speed, new_x, new_y)

            # Prevent from moving into blocked entity.
            if dest_entity.blocked:
                return

        # If destination is not blocked and is not a living Actor, move to it
        self.dest_x = new_x
        self.dest_y = new_y
        self._set_action(self.Actions.MOVE, self.move_speed)

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
    def attempt_wield(self, new_weapon: Optional[item.Item]) -> None:
        # Make sure attempting to wield an actual weapon.
        # Include None because that is fists.
        if (new_weapon is not None and not isinstance(new_weapon, weapon.Weapon)) and self.is_player:
            self.game_interface.message_box.add_msg(
                f"{self.name} cannot wield a {new_weapon.name}.", self.game_data.colors["ERROR_MSG"]
            )
            return

        # Finally set the action and send a message.
        self.action_target = new_weapon
        self._set_action(self.Actions.WIELD, self.wield_speed)

    # Checks for open doors around the Actor and closes them if they exist.
    def attempt_close_door(self) -> None:
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x != 0 or y != 0:
                    target_door: door.Door = self.game_entities.get_door_at(self.x + x, self.y + y)
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
