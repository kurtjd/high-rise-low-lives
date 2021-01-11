from __future__ import annotations
from typing import Any
import rendering
import input
import game_entities.entities
import game_entities.actor
import interface
import databases
import game_states


class GameEngine:
    """The game engine which handles states, input, rendering, etc."""

    def __init__(
            self,
            entities_: game_entities.entities.GameEntities,
            game_interface: interface.Interface,
            game_data: databases.Databases,
            player_: game_entities.actor.Player,
            map_size: tuple[int, int]
    ) -> None:
        self.entities = entities_
        self.game_interface = game_interface
        self.game_data = game_data
        self.player = player_

        self.playing_state: game_states.PlayingState = game_states.PlayingState(self)
        self.examine_state: game_states.ExamineState = game_states.ExamineState(self)
        self.select_target_state: game_states.SelectTargetState = game_states.SelectTargetState(self)
        self.select_throw_state: game_states.SelectThrowState = game_states.SelectThrowState(self)
        self.wield_screen_state: game_states.WieldScreenState = game_states.WieldScreenState(self)
        self.inventory_screen_state: game_states.InventoryScreenState = game_states.InventoryScreenState(self)
        self.throw_screen_state: game_states.ThrowScreenState = game_states.ThrowScreenState(self)
        self.drug_screen_state: game_states.DrugScreenState = game_states.DrugScreenState(self)
        self.charge_screen_state: game_states.ChargeScreenState = game_states.ChargeScreenState(self)
        self.desc_screen_state: game_states.DescScreenState = game_states.DescScreenState(self)

        self.state: game_states.BaseState = self.playing_state
        self.prev_states: list[game_states.BaseState] = []

        self.MAP_WIDTH: int = map_size[0]
        self.MAP_HEIGHT: int = map_size[1]

    def set_state(self, new_state: game_states.BaseState) -> None:
        """Sets the state the game is in."""

        self.state.exit()
        self.prev_states.append(self.state)
        self.state = new_state
        self.state.enter()

    def reverse_state(self) -> None:
        """Reverts the game to the previous state."""

        # If there isn't a previous state, then exit the game.
        if not self.prev_states:
            raise SystemExit()

        self.state.exit()
        self.state = self.prev_states.pop()
        self.state.enter()

    def handle_rendering(self, window: Any, surface: Any) -> None:
        """Handle all rendering for the game."""

        rendering.clear_surface(surface)
        self.state.handle_rendering(surface)
        rendering.present_surface(window, surface)

    def handle_input(self) -> None:
        """Handle all input for the game."""

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
        """Handle all updates for the game."""

        self.state.handle_updates()
