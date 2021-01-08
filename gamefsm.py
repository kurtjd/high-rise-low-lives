from typing import Optional, Any, Union
import rendering
import input
import entities
import interface


# A finite state machine used to manage state of game.
class GameFSM:
    def __init__(
            self,
            entities_: entities.GameEntities,
            game_interface: interface.Interface,
            player_: entities.Player,
            map_size: tuple[int, int]
    ) -> None:

        self.playing_state: PlayingState = PlayingState(
            self,
            entities_,
            game_interface,
            player_
        )

        self.examine_state: ExamineState = ExamineState(
            self,
            entities_,
            game_interface,
            player_
        )

        self.select_target_state: SelectTargetState = SelectTargetState(
            self,
            entities_,
            game_interface,
            player_
        )

        self.select_throw_state: SelectThrowState = SelectThrowState(
            self,
            entities_,
            game_interface,
            player_
        )

        self.wield_screen_state: WieldScreenState = WieldScreenState(
            self,
            entities_,
            game_interface,
            player_
        )

        self.inventory_screen_state: InventoryScreenState = InventoryScreenState(
            self,
            entities_,
            game_interface,
            player_
        )

        self.throw_screen_state: ThrowScreenState = ThrowScreenState(
            self,
            entities_,
            game_interface,
            player_
        )

        self.drug_screen_state: DrugScreenState = DrugScreenState(
            self,
            entities_,
            game_interface,
            player_
        )

        self.charge_screen_state: ChargeScreenState = ChargeScreenState(
            self,
            entities_,
            game_interface,
            player_
        )

        self.desc_screen_state: DescScreenState = DescScreenState(
            self,
            entities_,
            game_interface,
            player_
        )

        self.state: BaseState = self.playing_state
        self.prev_states: list[BaseState] = []

        self.MAP_WIDTH: int = map_size[0]
        self.MAP_HEIGHT: int = map_size[1]

    def set_state(self, new_state: "BaseState") -> None:
        self.state.exit()
        self.prev_states.append(self.state)
        self.state = new_state
        self.state.enter()

    def reverse_state(self) -> None:
        # If there isn't a previous state, then exit the game.
        if not self.prev_states:
            raise SystemExit()

        self.state.exit()
        self.state = self.prev_states.pop()
        self.state.enter()

    def handle_rendering(self, window: Any, surface: Any) -> None:
        rendering.clear_surface(surface)
        self.state.handle_rendering(surface)
        rendering.present_surface(window, surface)

    def handle_input(self) -> None:
        while 1:
            (event_type, event_key) = input.poll_input()

            if event_type == input.EventType.QUIT:
                raise SystemExit()
            elif event_type == input.EventType.KEYDOWN:
                self.state.handle_input(event_key)

                if event_key == input.Key.ESCAPE:
                    self.reverse_state()

                break

    def handle_updates(self) -> None:
        self.state.handle_updates()


# Common functionality of all states
class BaseState:
    def __init__(
            self,
            fsm: GameFSM,
            entities_: entities.GameEntities,
            game_interface: interface.Interface,
            player_: entities.Player
    ) -> None:
        self.fsm: GameFSM = fsm
        self.entities: entities.GameEntities = entities_
        self.game_interface: interface.Interface = game_interface
        self.player: entities.Player = player_

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_rendering(self, surface: Any) -> None:
        pass

    def handle_input(self, key: Union[input.Key, str]) -> None:
        pass

    def handle_updates(self) -> None:
        pass


# The state when the player is actually playing the game.
class PlayingState(BaseState):
    def __init__(
            self,
            fsm: GameFSM,
            entities_: entities.GameEntities,
            game_interface: interface.Interface,
            player_: entities.Player
    ) -> None:
        super().__init__(fsm, entities_, game_interface, player_)
        self.game_time: int = 0
        self.floor_on: int = 1

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_rendering(self, surface: Any) -> None:
        self.game_interface.stats_box.render(surface)
        self.game_interface.message_box.render(surface)
        self.entities.render_all(surface)

    def handle_input(self, key: Union[input.Key, str]) -> None:
        if key == input.Key.UP:
            self.player.attempt_move(0, -1)
        elif key == input.Key.DOWN:
            self.player.attempt_move(0, 1)
        elif key == input.Key.LEFT:
            self.player.attempt_move(-1, 0)
        elif key == input.Key.RIGHT:
            self.player.attempt_move(1, 0)
        elif key == input.Key.PERIOD:
            self.player.attempt_rest()
        elif key == input.Key.COMMA:
            self.player.attempt_pickup()
        elif key == input.Key.CTRL_C:
            self.player.attempt_close_door()
        elif key == 'w':
            self.fsm.set_state(self.fsm.wield_screen_state)
        elif key == 'i':
            self.fsm.set_state(self.fsm.inventory_screen_state)
        elif key == 'x':
            self.fsm.set_state(self.fsm.examine_state)
        elif key == 'f':
            self.fsm.set_state(self.fsm.select_target_state)
        elif key == 't':
            self.fsm.set_state(self.fsm.throw_screen_state)
        elif key == 'q':
            self.fsm.set_state(self.fsm.drug_screen_state)
        elif key == 'c':
            self.fsm.set_state(self.fsm.charge_screen_state)
        elif key == input.Key.ESCAPE:
            raise SystemExit()

    def handle_updates(self) -> None:
        # Updates the game every tick of time in between player actions
        while self.player.action_delay >= 0:
            self.game_time += 1
            self.entities.update_all(self.game_time)

        self.game_interface.stats_box.update(self.game_time, self.floor_on)


# The state where the player is in the wield menu.
class WieldScreenState(BaseState):
    def __init__(
            self,
            fsm: GameFSM,
            entities_: entities.GameEntities,
            game_interface: interface.Interface,
            player_: entities.Player
    ) -> None:
        super().__init__(fsm, entities_, game_interface, player_)

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_rendering(self, surface: Any) -> None:
        self.game_interface.wield_screen.render(surface, self.player.get_wieldable_items())

    def handle_input(self, key: Union[input.Key, str]) -> None:
        # The minus key unwields.
        if key == input.Key.MINUS:
            self.player.attempt_wield(None)
            self.fsm.reverse_state()

        for wieldable in self.player.get_wieldable_items():
            if wieldable[0] == key:
                self.player.attempt_wield(wieldable[1]["Item"])
                self.fsm.reverse_state()
                return

    def handle_updates(self) -> None:
        pass


class InventoryScreenState(BaseState):
    def __init__(
            self,
            fsm: GameFSM,
            entities_: entities.GameEntities,
            game_interface: interface.Interface,
            player_: entities.Player
    ) -> None:
        super().__init__(fsm, entities_, game_interface, player_)

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_rendering(self, surface: Any) -> None:
        self.game_interface.inventory_screen.render(surface, self.player)

    def handle_input(self, key: Union[input.Key, str]) -> None:
        for item in self.player.inventory.items():
            if item[0] == key:
                self.player.examine_target = item[1]["Item"]
                self.fsm.set_state(self.fsm.desc_screen_state)
                return

    def handle_updates(self) -> None:
        pass


class ThrowScreenState(BaseState):
    def __init__(
            self,
            fsm: GameFSM,
            entities_: entities.GameEntities,
            game_interface: interface.Interface,
            player_: entities.Player
    ) -> None:
        super().__init__(fsm, entities_, game_interface, player_)

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_rendering(self, surface: Any) -> None:
        self.game_interface.throw_screen.render(surface, self.player.get_throwable_items())

    def handle_input(self, key: Union[input.Key, str]) -> None:
        for throwable in self.player.get_throwable_items():
            if throwable[0] == key:
                self.player.item_selected = throwable[1]["Item"]
                self.fsm.set_state(self.fsm.select_throw_state)
                return

    def handle_updates(self) -> None:
        pass


class DescScreenState(BaseState):
    def __init__(
            self,
            fsm: GameFSM,
            entities_: entities.GameEntities,
            game_interface: interface.Interface,
            player_: entities.Player
    ) -> None:
        super().__init__(fsm, entities_, game_interface, player_)

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_rendering(self, surface: Any) -> None:
        self.game_interface.description_screen.render(surface, self.player.examine_target)

    def handle_input(self, key: Union[input.Key, str]) -> None:
        pass

    def handle_updates(self) -> None:
        pass


class DrugScreenState(BaseState):
    def __init__(
            self,
            fsm: GameFSM,
            entities_: entities.GameEntities,
            game_interface: interface.Interface,
            player_: entities.Player
    ) -> None:
        super().__init__(fsm, entities_, game_interface, player_)

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_rendering(self, surface: Any) -> None:
        self.game_interface.drug_screen.render(surface, self.player.get_drug_items())

    def handle_input(self, key: Union[input.Key, str]) -> None:
        for drug in self.player.get_drug_items():
            if drug[0] == key:
                self.player.attempt_use_drug(drug[0])
                self.fsm.set_state(self.fsm.playing_state)
                return

    def handle_updates(self) -> None:
        pass


class ChargeScreenState(BaseState):
    def __init__(
            self,
            fsm: GameFSM,
            entities_: entities.GameEntities,
            game_interface: interface.Interface,
            player_: entities.Player
    ) -> None:
        super().__init__(fsm, entities_, game_interface, player_)

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_rendering(self, surface: Any) -> None:
        self.game_interface.charge_screen.render(surface, self.player.get_power_sources())

    def handle_input(self, key: Union[input.Key, str]) -> None:
        for powersrc in self.player.get_power_sources():
            if powersrc[0] == key:
                self.player.attempt_charge(powersrc[0])
                self.fsm.set_state(self.fsm.playing_state)
                return

    def handle_updates(self) -> None:
        pass


# This state is when the player is selecting something on the map while playing.
class SelectState(PlayingState):
    def __init__(
            self,
            fsm: GameFSM,
            entities_: entities.GameEntities,
            game_interface: interface.Interface,
            player_: entities.Player
    ) -> None:
        super().__init__(fsm, entities_, game_interface, player_)

        # The location the player has his cursor over.
        self.select_x: int = self.player.x
        self.select_y: int = self.player.y

    def enter(self) -> None:
        self.select_x = self.player.x
        self.select_y = self.player.y
        self._highlight_entity((255, 255, 255))

    def exit(self) -> None:
        self._highlight_entity(None)

    def _highlight_entity(self, color: Optional[tuple[int, int, int]] = (255, 255, 255)) -> None:
        self.entities.get_top_entity_at(self.select_x, self.select_y).bgcolor = color

    def move_cursor(self, key: Union[input.Key, str]) -> None:
        if (key != input.Key.UP and key != input.Key.DOWN and
                key != input.Key.RIGHT and key != input.Key.LEFT):
            return

        if key == input.Key.UP:
            if self.select_y > 0:
                self._highlight_entity(None)
                self.select_y -= 1
                self._highlight_entity((255, 255, 255))
            else:
                return
        elif key == input.Key.DOWN:
            if self.select_y < (self.fsm.MAP_HEIGHT - 1):
                self._highlight_entity(None)
                self.select_y += 1
                self._highlight_entity((255, 255, 255))
            else:
                return
        elif key == input.Key.RIGHT:
            if self.select_x < (self.fsm.MAP_WIDTH - 1):
                self._highlight_entity(None)
                self.select_x += 1
                self._highlight_entity((255, 255, 255))
            else:
                return
        elif key == input.Key.LEFT:
            if self.select_x > 0:
                self._highlight_entity(None)
                self.select_x -= 1
                self._highlight_entity((255, 255, 255))
            else:
                return


# When the player is selecting something to examine.
class ExamineState(SelectState):
    def __init__(
            self,
            fsm: GameFSM,
            entities_: entities.GameEntities,
            game_interface: interface.Interface,
            player_: entities.Player
    ) -> None:
        super().__init__(fsm, entities_, game_interface, player_)

    def handle_input(self, key: Union[input.Key, str]) -> None:
        if key == 'v':
            self.player.examine_target = self.entities.get_top_entity_at(self.select_x, self.select_y)
            self.fsm.set_state(self.fsm.desc_screen_state)

        self.move_cursor(key)

    def handle_updates(self) -> None:
        pass


# When the player is something to attack ranged.
class SelectTargetState(SelectState):
    def __init__(
            self,
            fsm: GameFSM,
            entities_: entities.GameEntities,
            game_interface: interface.Interface,
            player_: entities.Player
    ) -> None:
        super().__init__(fsm, entities_, game_interface, player_)

    def enter(self) -> None:
        self.player.bullet_path = []
        super().enter()

    def handle_rendering(self, surface: Any) -> None:
        super().handle_rendering(surface)

        for point in self.player.bullet_path:
            rendering.render(surface, '*', point[0], point[1], (255, 0, 0))

    def update_bullet_path(self, extend: bool = False) -> None:
        self.player.bullet_path = self.player.get_line_of_sight(self.select_x, self.select_y, extend)

    def handle_input(self, key: Union[input.Key, str]) -> None:
        self.move_cursor(key)
        self.update_bullet_path(True)

        if key == input.Key.ENTER:
            self.player.attempt_atk(self.select_x, self.select_y, True, self.player.bullet_path)
            self.fsm.reverse_state()
        elif key == 'f':
            self.player.attempt_reload()
            self.fsm.reverse_state()

    def handle_updates(self) -> None:
        pass


class SelectThrowState(SelectTargetState):
    def __init__(
            self,
            fsm: GameFSM,
            entities_: entities.GameEntities,
            game_interface: interface.Interface,
            player_: entities.Player
    ) -> None:
        super().__init__(fsm, entities_, game_interface, player_)

    def handle_input(self, key: Union[input.Key, str]) -> None:
        self.move_cursor(key)
        self.update_bullet_path(False)

        if key == input.Key.ENTER:
            self.player.attempt_throw(self.select_x, self.select_y, self.player.item_selected, self.player.bullet_path)
            self.fsm.set_state(self.fsm.playing_state)
