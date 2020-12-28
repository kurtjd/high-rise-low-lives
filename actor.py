import entity
import globals
import weapon
import door
from enum import Enum, auto


class Actor(entity.Entity):

    # Actors can be performing one of these actions:
    class Actions(Enum):
        MOVE = auto(),
        ATK_MELEE = auto(),
        WIELD = auto(),
        OPEN_DOOR = auto(),
        CLOSE_DOOR = auto(),
        REST = auto(),
        PICKUP = auto()

    # ~~~ PRIVATE METHODS ~~~

    def __init__(self, name, race, class_name, desc, x, y, health, muscle, smarts, reflexes, wits, grit,
                 ai, is_player, graphic, color, game_data, game_entities, game_interface):
        super().__init__(x, y, True, graphic, color, game_entities)

        # Notes if this actor is the player or not.
        self.is_player = is_player

        self.game_data = game_data
        self.game_entities = game_entities
        self.game_interface = game_interface

        # Descriptors of Actor
        self.name = name
        self.desc = desc
        self.ai = ai  # This contains a function name corresponding to one of the AI functions in ai.py
        self.race = race
        self.class_name = class_name

        # Attributes and stats of Actor
        self.health = health
        self.muscle = muscle
        self.smarts = smarts
        self.reflexes = reflexes
        self.wits = wits
        self.grit = grit
        self.base_atk_dmg = 10

        # Inventory and currently equipped stuff
        self.inventory = []
        self.wielding = None
        self.wearing = None

        # These are the speeds it takes the Actor to perform different actions
        # The lower the better
        # Hard-coded for now.
        self.move_speed = 10
        self.atk_speed = 10
        self.wield_speed = 5
        self.gen_speed = 5  # For general actions such as opening doors.
        self.atk_dmg = self.base_atk_dmg

        # How many turns it takes to recover some stats.
        self.recovery_rate = 10

        # These variables are used to track actions.
        self.action_target = None  # Used when the target isn't an x/y
        self.action_delay = -1
        self.action_target_x = None
        self.action_target_y = None
        self.action = 0
        self.dest_x = None
        self.dest_y = None

        self.atk_target = None

        # Set a default action. For now, just rest.
        if not is_player:
            self.__set_action(self.Actions.REST, globals.REST_TIME)

        game_entities.actors.append(self)

    # Let the AI think of a new action.
    def __think(self):
        # This uses the function name stored in self.ai to call one of the AI functions and passes self
        self.ai(self, self.game_entities.actors)

    # Finds the correct a-zA-Z character to assign as an id to a newly acquired item.
    def __get_next_item_id(self):
        # Item IDs can be a-zA-Z so loop through all ASCII numbers skipping the non-alpha in between.
        for item_id in range(65, 123):
            if 91 <= item_id <= 96:
                continue

            # For each potential item id, check if an existing item already has that id. If not, then assign as new id.
            empty_id = True
            for exist_item in self.inventory:
                if exist_item["ID"] == chr(item_id):
                    empty_id = False
                    break
            if empty_id:
                return chr(item_id)

    # Actors can potentially be reanimated so it is only "playing" dead
    def __play_dead(self):
        self.graphic = self.game_data.tiles["CORPSE"]["Character"]
        self.color = self.game_data.tiles["CORPSE"]["Color"]
        self.blocked = self.game_data.tiles["CORPSE"]["Blocked"]

    # Moves to a new position.
    def __move(self):
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

    # Attempts to open a door
    def __open_door(self):
        target_door = self.game_entities.get_door_at(self.action_target_x, self.action_target_y)
        if not target_door.locked:
            target_door.open()
        else:
            self.game_interface.message_box.add_msg(
                f"That door is locked.", self.game_data.colors["ERROR_MSG"]
            )

    # Performs a melee attack
    def __attack_melee(self):
        target_actor = self.game_entities.get_actor_at(self.action_target_x, self.action_target_y)
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
        target_actor.health -= self.atk_dmg

        # Send different message depending on what is attacked with.
        # Change color depending on if player or not.
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

    # Update what the player is wielding and change stats to reflect that.
    def __wield(self):
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
    def __close_door(self):
        target_door = self.game_entities.get_door_at(self.action_target_x, self.action_target_y)
        target_door.close()

    # Actually rests
    # Essentially does nothing.
    def __rest(self):
        pass

    # Recovers stats
    def __recover(self):
        self.health += 1
        if self.health > 100:
            self.health = 100

    # Actually picks up an item.
    def __pick_up(self):
        # Get all items at target and ask which to pick-up
        # For now just pick up first item
        items_at_pos = self.game_entities.get_items_at(self.action_target_x, self.action_target_y)
        item = items_at_pos[0].actor_pick_up(self)

        self.game_interface.message_box.add_msg(
            f"{self.name} picks up a {item.name}.", self.game_data.colors["SUCCESS_MSG"]
        )

    # Queues an action and sets the delay and target of the action.
    def __set_action(self, action, delay, target_x=None, target_y=None):
        self.action = action
        self.action_delay = delay
        self.action_target_x = target_x
        self.action_target_y = target_y

    # Called after action is performed. Resets all counters and associated variables.
    def __reset_action(self):
        self.action = None
        self.action_target_x = None
        self.action_target_y = None
        self.action_delay = -1  # -1 represents no action queued
        self.dest_x = None
        self.dest_y = None

        # Allow the AI to think of a new action.
        if not self.is_player:
            self.__think()

    # Actually performs the action by calling the appropriate method.
    def __do_action(self):
        if self.action == self.Actions.ATK_MELEE:
            self.__attack_melee()
        elif self.action == self.Actions.MOVE:
            self.__move()
        elif self.action == self.Actions.OPEN_DOOR:
            self.__open_door()
        elif self.action == self.Actions.CLOSE_DOOR:
            self.__close_door()
        elif self.action == self.Actions.REST:
            self.__rest()
        elif self.action == self.Actions.PICKUP:
            self.__pick_up()
        elif self.action == self.Actions.WIELD:
            self.__wield()

    # ~~~ PUBLIC METHODS ~~~

    # Adds an item to the inventory
    def add_inventory(self, item, amount=1):
        self.inventory.append(dict({"ID": self.__get_next_item_id(), "Item": item, "Amount": amount}))

    # Returns a list of wieldable items from actors inventory.
    def get_wieldable_items(self):
        wieldables = []
        for item in self.inventory:
            if isinstance(item["Item"], weapon.Weapon):
                wieldables.append(item)

        return wieldables

    # Makes sure the Actor can actually move to where it wants to go.
    def attempt_move(self, x, y):
        # The destination the actor is attempting to move to
        new_x = self.x + x
        new_y = self.y + y

        # We want to check what entites are occupying the move destination
        dest_entities = self.game_entities.get_all_at(new_x, new_y)
        for dest_entity in dest_entities:
            # Check to see if destination has an Actor, if so perform melee attack
            if isinstance(dest_entity, Actor):
                self.__set_action(self.Actions.ATK_MELEE, self.atk_speed, new_x, new_y)
            elif isinstance(dest_entity, door.Door) and not dest_entity.opened:
                self.__set_action(self.Actions.OPEN_DOOR, self.gen_speed, new_x, new_y)

            # Prevent from moving into blocked entity.
            if dest_entity.blocked:
                return

        # If destination is not blocked and is not a living Actor, move to it
        self.dest_x = new_x
        self.dest_y = new_y
        self.__set_action(self.Actions.MOVE, self.move_speed)

    # Attempts to pick an item up off the floor where the Actor is standing.
    def attempt_pickup(self):
        # Only pick up if there's something on the floor.
        if self.game_entities.get_items_at(self.x, self.y):
            self.__set_action(self.Actions.PICKUP, self.gen_speed, self.x, self.y)
        elif self.is_player:
            self.game_interface.message_box.add_msg(
                "There's nothing here to pickup.", self.game_data.colors["ERROR_MSG"]
            )

    # Wields a new weapon
    def attempt_wield(self, new_weapon):
        # Make sure attempting to wield an actual weapon.
        # Include None because that is fists.
        if (new_weapon is not None and not isinstance(new_weapon, weapon.Weapon)) and self.is_player:
            self.game_interface.message_box.add_msg(
                f"{self.name} cannot wield a {new_weapon.name}.", self.game_data.colors["ERROR_MSG"]
            )
            return

        # Finally set the action and send a message.
        self.action_target = new_weapon
        self.__set_action(self.Actions.WIELD, self.wield_speed)

    # Checks for open doors around the Actor and closes them if they exist.
    def attempt_close_door(self):
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x != 0 or y != 0:
                    target_door = self.game_entities.get_door_at(self.x + x, self.y + y)
                    if target_door is not None and target_door.opened:
                        self.__set_action(self.Actions.CLOSE_DOOR, self.gen_speed, target_door.x, target_door.y)
                        return

        if self.is_player:
            self.game_interface.message_box.add_msg(
                "There's no door to be closed here.", self.game_data.colors["ERROR_MSG"]
            )

    # Actor rests to recover HP and other stuff
    def attempt_rest(self):
        self.__set_action(self.Actions.REST, globals.REST_TIME)

    # Called every tick of game time.
    def update(self):
        # If the actor is dead, show it as a passable corpse and do nothing
        if self.health <= 0:
            self.__play_dead()
            return

        # Check if time to recover
        if globals.time > 0 and (globals.time % self.recovery_rate) == 0:
            self.__recover()

        # Only delay action if the actor has an action queued
        if self.action_delay > 0:
            self.action_delay -= 1

            # On the penultimate tick, perform the action
            if self.action_delay == 1:
                self.__do_action()
            # Once the Actor has performed its action, reset everything
            elif self.action_delay == 0:
                self.__reset_action()
