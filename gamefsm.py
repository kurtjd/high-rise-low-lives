import tcod


# A finite state machine used to manage state of game.
class GameFSM:
    def __init__(self, game_entities, game_interface, player):
        self.playing_state = PlayingState(self, game_entities, game_interface, player)
        self.examine_state = ExamineState(self, game_entities, game_interface, player)
        self.select_target_state = SelectTargetState(self, game_entities, game_interface, player)
        self.wield_screen_state = WieldScreenState(self, game_interface, player)
        self.inventory_screen_state = InventoryScreenState(self, game_interface, player)
        self.desc_screen_state = DescScreenState(game_interface, player)

        self.state = self.playing_state
        self.prev_states = []

    def set_state(self, new_state):
        self.state.exit()
        self.prev_states.append(self.state)
        self.state = new_state
        self.state.enter()

    def reverse_state(self):
        # If there isn't a previous state, then exit the game.
        if not self.prev_states:
            raise SystemExit()

        self.state.exit()
        self.state = self.prev_states.pop()
        self.state.enter()

    def handle_rendering(self, window, console):
        self.state.handle_rendering(console)

        # General rendering.
        window.present(console)
        console.clear()

    def handle_input(self):
        for event in tcod.event.wait():
            if event.type == "QUIT":
                raise SystemExit()
            elif event.type == "KEYDOWN":
                key = event.sym

                self.state.handle_input(event)

                # General input
                if key == tcod.event.K_ESCAPE:
                    self.reverse_state()

    def handle_updates(self):
        self.state.handle_updates()


# Common functionality of all states
class BaseState:
    # Put the common input code in handle_input and make it work?
    pass


# The state when the player is actually playing the game.
class PlayingState(BaseState):
    def __init__(self, fsm, game_entities, game_interface, player):
        self.fsm = fsm
        self.game_entities = game_entities
        self.game_interface = game_interface
        self.player = player

        self.game_time = 0
        self.floor_on = 1

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_rendering(self, console):
        self.game_interface.stats_box.render(console)
        self.game_interface.message_box.render(console)
        self.game_entities.render_all(console)

    def handle_input(self, event):
        key = event.sym

        if key == tcod.event.K_UP:
            self.player.attempt_move(0, -1)
        elif key == tcod.event.K_DOWN:
            self.player.attempt_move(0, 1)
        elif key == tcod.event.K_LEFT:
            self.player.attempt_move(-1, 0)
        elif key == tcod.event.K_RIGHT:
            self.player.attempt_move(1, 0)
        elif key == tcod.event.K_PERIOD:
            self.player.attempt_rest()
        elif key == tcod.event.K_SEMICOLON:
            self.player.attempt_pickup()
        elif (event.mod & tcod.event.KMOD_CTRL) and key == tcod.event.K_c:
            self.player.attempt_close_door()
        elif key == tcod.event.K_w:
            self.fsm.set_state(self.fsm.wield_screen_state)
        elif key == tcod.event.K_i:
            self.fsm.set_state(self.fsm.inventory_screen_state)
        elif key == tcod.event.K_x:
            self.fsm.set_state(self.fsm.examine_state)

    def handle_updates(self):
        self.game_interface.stats_box.update(self.game_time, self.floor_on)

        # Updates the game every tick of time in between player actions
        while self.player.action_delay >= 0:
            self.game_time += 1
            self.game_entities.update_all(self.game_time)


# The state where the player is in the wield menu.
class WieldScreenState(BaseState):
    def __init__(self, fsm, game_interface, player):
        self.fsm = fsm
        self.game_interface = game_interface
        self.player = player

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_rendering(self, console):
        self.game_interface.wield_screen.render(console, self.player.get_wieldable_items())

    def handle_input(self, event):
        key = event.sym

        # The minus (-) key makes the player unarmed.
        if key == tcod.event.K_MINUS:
            self.player.attempt_wield(None)
            self.fsm.set_state(self.fsm.playing_state)

        # If not a letter key, then do nothing.
        elif tcod.event.K_a <= key <= tcod.event.K_z:
            key = chr(key)

            # If the shift key was held, convert to upper-case.
            if event.mod & tcod.event.KMOD_SHIFT:
                key = key.upper()

            # Search the IDs of the player's wieldables for a match with the key pressed and then wield that.
            for wieldable in self.player.get_wieldable_items():
                if wieldable["ID"] == key:
                    self.player.attempt_wield(wieldable["Item"])
                    self.fsm.set_state(self.fsm.playing_state)
                    return

    def handle_updates(self):
        pass


class InventoryScreenState(BaseState):
    def __init__(self, fsm, game_interface, player):
        self.fsm = fsm
        self.game_interface = game_interface
        self.player = player

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_rendering(self, console):
        self.game_interface.inventory_screen.render(console, self.player)

    def handle_input(self, event):
        key = event.sym

        # If not a letter key, then do nothing.
        if tcod.event.K_a <= key <= tcod.event.K_z:
            key = chr(key)

            # If the shift key was held, convert to upper-case.
            if event.mod & tcod.event.KMOD_SHIFT:
                key = key.upper()

            # Search the IDs of the player's inventory for a match with the key pressed and then describe that.
            for item in self.player.inventory:
                if item["ID"] == key:
                    self.player.examine_target = item["Item"]
                    self.fsm.set_state(self.fsm.desc_screen_state)
                    return

    def handle_updates(self):
        pass


class DescScreenState(BaseState):
    def __init__(self, game_interface, player):
        self.game_interface = game_interface
        self.player = player

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_rendering(self, console):
        self.game_interface.description_screen.render(console, self.player.examine_target)

    def handle_input(self, event):
        pass

    def handle_updates(self):
        pass


class ExamineState(PlayingState):
    def __init__(self, fsm, game_entities, game_interface, player):
        super().__init__(fsm, game_entities, game_interface, player)
        self.player = player
        self.game_entities = game_entities

        # The location the player has his cursor over.
        self.examine_loc_x = self.player.x
        self.examine_loc_y = self.player.y

    def __highlight_entity(self, color):
        self.game_entities.get_all_at(self.examine_loc_x, self.examine_loc_y)[0].bgcolor = color

    def enter(self):
        self.examine_loc_x = self.player.x
        self.examine_loc_y = self.player.y
        self.__highlight_entity(tcod.white)

    def exit(self):
        self.__highlight_entity(None)

    def handle_rendering(self, console):
        # This substate doesn't have its own rendering
        super().handle_rendering(console)

    def handle_input(self, event):
        key = event.sym

        # Clean this up
        if key == tcod.event.K_v:
            self.player.examine_target = self.game_entities.get_all_at(self.examine_loc_x, self.examine_loc_y)[1]
            self.fsm.set_state(self.fsm.desc_screen_state)

        if (key != tcod.event.K_UP and key != tcod.event.K_DOWN and
                key != tcod.event.K_RIGHT and key != tcod.event.K_LEFT):
            return

        self.__highlight_entity(None)
        if key == tcod.event.K_UP:
            self.examine_loc_y -= 1
        elif key == tcod.event.K_DOWN:
            self.examine_loc_y += 1
        elif key == tcod.event.K_RIGHT:
            self.examine_loc_x += 1
        elif key == tcod.event.K_LEFT:
            self.examine_loc_x -= 1
        self.__highlight_entity(tcod.white)

    def handle_updates(self):
        pass


class SelectTargetState(PlayingState):
    def __init__(self, fsm, game_entities, game_interface, player):
        super().__init__(fsm, game_entities, game_interface, player)
        self.player = player
        self.game_entities = game_entities

        # The location the player has his cursor over.
        self.target_x = self.player.x
        self.target_y = self.player.y

    def __highlight_entity(self, color):
        self.game_entities.get_all_at(self.target_x, self.target_y)[0].bgcolor = color

    def enter(self):
        self.target_x = self.player.x
        self.target_y = self.player.y
        self.__highlight_entity(tcod.white)

    def exit(self):
        self.__highlight_entity(None)

    def handle_rendering(self, console):
        # This substate doesn't have its own rendering
        super().handle_rendering(console)

    def handle_input(self, event):
        key = event.sym

        # Clean this up
        if key == tcod.event.K_KP_ENTER:
            pass

        if (key != tcod.event.K_UP and key != tcod.event.K_DOWN and
                key != tcod.event.K_RIGHT and key != tcod.event.K_LEFT):
            return

        self.__highlight_entity(None)
        if key == tcod.event.K_UP:
            self.target_y -= 1
        elif key == tcod.event.K_DOWN:
            self.target_y += 1
        elif key == tcod.event.K_RIGHT:
            self.target_x += 1
        elif key == tcod.event.K_LEFT:
            self.target_x -= 1
        self.__highlight_entity(tcod.white)

    def handle_updates(self):
        pass
