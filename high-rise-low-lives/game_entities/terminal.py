from __future__ import annotations
from enum import Enum, auto
import databases
import interface
from .entities import GameEntities
from .entity import Entity
from .actor import Actor


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
        tile_: dict = game_data.tiles["TERMINAL"]

        super().__init__(x, y, tile_["Name"], tile_["Desc"], tile_["Blocked"],
                         tile_["Character"], tile_["Color"], game_data, game_entities_, game_interface)

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

        for door_ in self.game_entities.doors:
            door_.locked = False

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
