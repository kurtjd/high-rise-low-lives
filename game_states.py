from typing import Any, Union, Optional
import game_engine
import entities
import rendering
import input


class BaseState:
    """Common functionality of all states."""

    def __init__(self, engine: "game_engine.GameEngine") -> None:
        self.engine = engine

    def enter(self) -> None:
        """Called when the state is entered."""

        pass

    def exit(self) -> None:
        """Called when the state is exited."""

        pass

    def handle_rendering(self, surface: Any) -> None:
        """Handles rendering for this specific state."""

        pass

    def handle_input(self, key: Union[input.Key, str]) -> None:
        """Handles input for this specific state."""

        pass

    def handle_updates(self) -> None:
        """Handles updates for this specific state."""

        pass


class PlayingState(BaseState):
    """The state when the player is actually playing the game."""

    def __init__(self, engine: "game_engine.GameEngine") -> None:
        super().__init__(engine)

        self.game_time: int = 0
        self.floor_on: int = 1

    def handle_rendering(self, surface: Any) -> None:
        """Handles rendering for the Playing state."""

        self.engine.game_interface.stats_box.render(surface)
        self.engine.game_interface.message_box.render(surface)
        self.engine.entities.render_all(surface)

    def handle_input(self, key: Union[input.Key, str]) -> None:
        """Handles input for the Playing state."""

        if key == input.Key.UP:
            self.engine.player.attempt_move(0, -1)
        elif key == input.Key.DOWN:
            self.engine.player.attempt_move(0, 1)
        elif key == input.Key.LEFT:
            self.engine.player.attempt_move(-1, 0)
        elif key == input.Key.RIGHT:
            self.engine.player.attempt_move(1, 0)
        elif key == input.Key.PERIOD:
            self.engine.player.attempt_rest()
        elif key == input.Key.COMMA:
            self.engine.player.attempt_pickup()
        elif key == input.Key.CTRL_C:
            self.engine.player.attempt_close_door()
        elif key == 'w':
            self.engine.set_state(self.engine.wield_screen_state)
        elif key == 'i':
            self.engine.set_state(self.engine.inventory_screen_state)
        elif key == 'x':
            self.engine.set_state(self.engine.examine_state)
        elif key == 'f':
            self.engine.set_state(self.engine.select_target_state)
        elif key == 't':
            self.engine.set_state(self.engine.throw_screen_state)
        elif key == 'q':
            self.engine.set_state(self.engine.drug_screen_state)
        elif key == 'c':
            self.engine.set_state(self.engine.charge_screen_state)
        elif key == input.Key.ESCAPE:
            raise SystemExit()

    def handle_updates(self) -> None:
        """Handles updates for the Playing state."""

        # Updates the game every round while the player cools down from action.
        while self.engine.player.action_cooldown >= 0:
            self.game_time += 1
            self.engine.entities.update_all(self.game_time)

        self.engine.game_interface.stats_box.update(self.game_time, self.floor_on)


class WieldScreenState(BaseState):
    """The state where the player is in the wield menu."""

    def __init__(self, engine: "game_engine.GameEngine") -> None:
        super().__init__(engine)

    def handle_rendering(self, surface: Any) -> None:
        """Handles rendering for the WieldScreen state."""

        self.engine.game_interface.wield_screen.render(surface, self.engine.player.get_wieldable_items())

    def handle_input(self, key: Union[input.Key, str]) -> None:
        """Handles input for the WieldScreen state."""

        # The minus key unwields.
        if key == input.Key.MINUS:
            self.engine.player.attempt_wield(None)
            self.engine.reverse_state()

        for wieldable in self.engine.player.get_wieldable_items():
            if wieldable[0] == key:
                self.engine.player.attempt_wield(wieldable[1]["Item"])
                self.engine.reverse_state()
                return


class InventoryScreenState(BaseState):
    """The state when the player is viewing inventory."""

    def __init__(self, engine: "game_engine.GameEngine") -> None:
        super().__init__(engine)

    def handle_rendering(self, surface: Any) -> None:
        """Handles rendering for the InventoryScreen state."""

        self.engine.game_interface.inventory_screen.render(surface, self.engine.player)

    def handle_input(self, key: Union[input.Key, str]) -> None:
        """Handles input for the InventoryScreen state."""

        for item in self.engine.player.inventory.items():
            if item[0] == key:
                self.engine.player.examine_target = item[1]["Item"]
                self.engine.set_state(self.engine.desc_screen_state)
                return


class ThrowScreenState(BaseState):
    """The state when the player is selecting something to throw."""

    def __init__(self, engine: "game_engine.GameEngine") -> None:
        super().__init__(engine)

    def handle_rendering(self, surface: Any) -> None:
        """Handles rendering for the ThrowScreen state."""

        self.engine.game_interface.throw_screen.render(surface, self.engine.player.get_throwable_items())

    def handle_input(self, key: Union[input.Key, str]) -> None:
        """Handles input for the ThrowScreen state."""

        for throwable in self.engine.player.get_throwable_items():
            if throwable[0] == key:
                self.engine.player.item_selected = throwable[1]["Item"]
                self.engine.set_state(self.engine.select_throw_state)
                return


class DescScreenState(BaseState):
    """The state when the player is viewing the description of something."""

    def __init__(self, engine: "game_engine.GameEngine") -> None:
        super().__init__(engine)

    def handle_rendering(self, surface: Any) -> None:
        """Handles rendering for the DescScreen state."""

        self.engine.game_interface.description_screen.render(surface, self.engine.player.examine_target)


class DrugScreenState(BaseState):
    """The state when the player is selecting a drug to use."""

    def __init__(self, engine: "game_engine.GameEngine") -> None:
        super().__init__(engine)

    def handle_rendering(self, surface: Any) -> None:
        """Handles rendering for the DrugScreen state."""

        self.engine.game_interface.drug_screen.render(surface, self.engine.player.get_drug_items())

    def handle_input(self, key: Union[input.Key, str]) -> None:
        """Handles input for the DrugScreen state."""

        for drug in self.engine.player.get_drug_items():
            if drug[0] == key:
                self.engine.player.attempt_use_drug(drug[0])
                self.engine.set_state(self.engine.playing_state)
                return


class ChargeScreenState(BaseState):
    """The state when the player is selecting something to charge up with."""

    def __init__(self, engine: "game_engine.GameEngine") -> None:
        super().__init__(engine)

    def handle_rendering(self, surface: Any) -> None:
        """Handles rendering for the ChargeScreen state."""

        self.engine.game_interface.charge_screen.render(surface, self.engine.player.get_power_sources())

    def handle_input(self, key: Union[input.Key, str]) -> None:
        """Handles input for the ChargeScreen state."""

        for powersrc in self.engine.player.get_power_sources():
            if powersrc[0] == key:
                self.engine.player.attempt_charge(powersrc[0])
                self.engine.set_state(self.engine.playing_state)
                return


class SelectState(PlayingState):
    """The state when the player is selecting something on the map while playing."""

    def __init__(self, engine: "game_engine.GameEngine") -> None:
        super().__init__(engine)

        # The location the player has his cursor over.
        self.select_x: int = self.engine.player.x
        self.select_y: int = self.engine.player.y

    def _highlight_entity(self, color: Optional[tuple[int, int, int]]) -> None:
        """Sets the background color of a selected entity in order to 'highlight' it."""

        top_entity: entities.Entity = self.engine.entities.get_top_entity_at(self.select_x, self.select_y, True)
        top_entity.highlight(color)

    def enter(self) -> None:
        """Called when the Select state is entered."""

        self.select_x = self.engine.player.x
        self.select_y = self.engine.player.y
        self._highlight_entity(self.engine.game_data.colors["HIGHLIGHT"])

    def exit(self) -> None:
        """Called when the Select state is exited."""

        self._highlight_entity(None)

    def move_cursor(self, key: Union[input.Key, str]) -> None:
        """Moves a 'cursor' by highlighting an entity as the user presses the arrow keys."""

        if (key != input.Key.UP and key != input.Key.DOWN and
                key != input.Key.RIGHT and key != input.Key.LEFT):
            return

        if key == input.Key.UP:
            if self.select_y > 0:
                self._highlight_entity(None)
                self.select_y -= 1
                self._highlight_entity(self.engine.game_data.colors["HIGHLIGHT"])
            else:
                return
        elif key == input.Key.DOWN:
            if self.select_y < (self.engine.MAP_HEIGHT - 1):
                self._highlight_entity(None)
                self.select_y += 1
                self._highlight_entity(self.engine.game_data.colors["HIGHLIGHT"])
            else:
                return
        elif key == input.Key.RIGHT:
            if self.select_x < (self.engine.MAP_WIDTH - 1):
                self._highlight_entity(None)
                self.select_x += 1
                self._highlight_entity(self.engine.game_data.colors["HIGHLIGHT"])
            else:
                return
        elif key == input.Key.LEFT:
            if self.select_x > 0:
                self._highlight_entity(None)
                self.select_x -= 1
                self._highlight_entity(self.engine.game_data.colors["HIGHLIGHT"])
            else:
                return


class ExamineState(SelectState):
    """The state when the player is selecting something to examine while playing."""

    def __init__(self, engine: "game_engine.GameEngine") -> None:
        super().__init__(engine)

    def handle_input(self, key: Union[input.Key, str]) -> None:
        """Handles input for the Examine state."""

        if key == 'v':
            self.engine.player.examine_target = \
                self.engine.entities.get_top_entity_at(self.select_x, self.select_y, True)
            self.engine.set_state(self.engine.desc_screen_state)

        self.move_cursor(key)


class SelectTargetState(SelectState):
    """The state when the player is selecting something to attack with a ranged or thrown weapon."""

    def __init__(self, engine: "game_engine.GameEngine") -> None:
        super().__init__(engine)

    def update_bullet_path(self, extend: bool = False) -> None:
        """ Updates the player's bullet path."""

        self.engine.player.bullet_path = \
            self.engine.player.get_line_of_sight(self.select_x, self.select_y, extend)

    def enter(self) -> None:
        """Called when the SelectTarget state is entered."""

        self.engine.player.bullet_path = []
        super().enter()

    def handle_rendering(self, surface: Any) -> None:
        """Handles rendering for the SelectTarget state."""

        super().handle_rendering(surface)

        # Draws a line along the bullet path.
        for point in self.engine.player.bullet_path:
            # Later remove hard-coded color and character.
            rendering.render(surface, '*', point[0], point[1], self.engine.game_data.colors["RED"])

    def handle_input(self, key: Union[input.Key, str]) -> None:
        """Handles input for the SelectTarget state."""

        self.move_cursor(key)
        self.update_bullet_path(True)

        if key == input.Key.ENTER:
            self.engine.reverse_state()
            self.engine.player.attempt_atk(self.select_x, self.select_y, True, self.engine.player.bullet_path)
        elif key == 'f':
            self.engine.reverse_state()
            self.engine.player.attempt_reload()


class SelectThrowState(SelectTargetState):
    """The state when the player is selecting a target to throw an item at."""

    def __init__(self, engine: "game_engine.GameEngine") -> None:
        super().__init__(engine)

    def handle_input(self, key: Union[input.Key, str]) -> None:
        self.move_cursor(key)
        self.update_bullet_path(False)

        if key == input.Key.ENTER:
            self.engine.set_state(self.engine.playing_state)
            self.engine.player.attempt_throw(self.select_x, self.select_y, self.engine.player.item_selected,
                                             self.engine.player.bullet_path)
