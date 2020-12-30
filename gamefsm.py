import tcod


# A finite state machine used to manage state of game.
class GameFSM:
    def __init__(self, game_entities, game_interface, player, map_size):
        self.playing_state = PlayingState(self, game_entities, game_interface, player)
        self.examine_state = ExamineState(self, game_entities, game_interface, player)
        self.select_target_state = SelectTargetState(self, game_entities, game_interface, player)
        self.wield_screen_state = WieldScreenState(self, game_interface, player)
        self.inventory_screen_state = InventoryScreenState(self, game_interface, player)
        self.desc_screen_state = DescScreenState(game_interface, player)

        self.state = self.playing_state
        self.prev_states = []

        self.MAP_WIDTH = map_size[0]
        self.MAP_HEIGHT = map_size[1]

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
        elif key == tcod.event.K_f:
            self.fsm.set_state(self.fsm.select_target_state)

    def handle_updates(self):
        # Updates the game every tick of time in between player actions
        while self.player.action_delay >= 0:
            self.game_time += 1
            self.game_entities.update_all(self.game_time)

        self.game_interface.stats_box.update(self.game_time, self.floor_on)


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
            self.fsm.reverse_state()

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
                    self.fsm.reverse_state()
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


# This state is when the player is selecting something on the map while playing.
class SelectState(PlayingState):
    def __init__(self, fsm, game_entities, game_interface, player):
        super().__init__(fsm, game_entities, game_interface, player)

        # The location the player has his cursor over.
        self.select_x = self.player.x
        self.select_y = self.player.y

    def enter(self):
        self.select_x = self.player.x
        self.select_y = self.player.y
        self._highlight_entity(tcod.white)

    def exit(self):
        self._highlight_entity(None)

    def _highlight_entity(self, color):
        self.game_entities.get_all_at(self.select_x, self.select_y)[0].bgcolor = color

    def move_cursor(self, key):
        if (key != tcod.event.K_UP and key != tcod.event.K_DOWN and
                key != tcod.event.K_RIGHT and key != tcod.event.K_LEFT):
            return

        if key == tcod.event.K_UP:
            if self.select_y > 0:
                self._highlight_entity(None)
                self.select_y -= 1
                self._highlight_entity(tcod.white)
            else:
                return
        elif key == tcod.event.K_DOWN:
            if self.select_y < (self.fsm.MAP_HEIGHT - 1):
                self._highlight_entity(None)
                self.select_y += 1
                self._highlight_entity(tcod.white)
            else:
                return
        elif key == tcod.event.K_RIGHT:
            if self.select_x < (self.fsm.MAP_WIDTH - 1):
                self._highlight_entity(None)
                self.select_x += 1
                self._highlight_entity(tcod.white)
            else:
                return
        elif key == tcod.event.K_LEFT:
            if self.select_x > 0:
                self._highlight_entity(None)
                self.select_x -= 1
                self._highlight_entity(tcod.white)
            else:
                return


# When the player is selecting something to examine.
class ExamineState(SelectState):
    def __init__(self, fsm, game_entities, game_interface, player):
        super().__init__(fsm, game_entities, game_interface, player)

    def handle_input(self, event):
        key = event.sym

        if key == tcod.event.K_v:
            self.player.examine_target = self.game_entities.get_all_at(self.select_x, self.select_y)[-1]
            self.fsm.set_state(self.fsm.desc_screen_state)

        self.move_cursor(key)

    def handle_updates(self):
        pass


# When the player is something to attack ranged.
class SelectTargetState(SelectState):
    def __init__(self, fsm, game_entities, game_interface, player):
        super().__init__(fsm, game_entities, game_interface, player)
        self.bullet_path = []

    def enter(self):
        self.bullet_path = []
        super().enter()

    # Uses the bresenham line algorithm to get a list of points on the map the bullet would pass through.
    def _set_bullet_path(self, x1, y1, x2, y2):
        path = tcod.los.bresenham((x1, y1), (x2, y2)).tolist()[1:]  # Disclude the player from the bullet path.
        new_path = []

        # Check each point in the path for a blocked entity. If so, stop the bullet path there.
        for point in path:
            new_path.append(point)
            self.bullet_path = new_path
            for entity in self.game_entities.get_all_at(point[0], point[1]):
                if entity.blocked:
                    return

    def handle_rendering(self, console):
        super().handle_rendering(console)

        for point in self.bullet_path:
            console.print(point[0], point[1], '*', tcod.red)

    def handle_input(self, event):
        key = event.sym

        self.move_cursor(key)
        self._set_bullet_path(self.player.x, self.player.y, self.select_x, self.select_y)

        if key == tcod.event.K_RETURN:
            self.player.attempt_atk(self.select_x, self.select_y, True, self.bullet_path)
            self.fsm.reverse_state()

    def handle_updates(self):
        pass
