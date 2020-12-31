from enum import Enum, auto
import entity
import actor
import game_entities
import interface
import databases


# Terminals can be hacked to do things like:
# open doors, turn off security cameras, disable turrets and traps, download programs, etc
# If failed to hack, can do nasty things like sound an alarm, explode, give you a virus, etc
class Terminal(entity.Entity):
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
            game_entities_: "game_entities.GameEntities",
            game_interface: interface.Interface
    ) -> None:
        tile: dict = game_data.tiles["TERMINAL"]
        super().__init__(x, y, tile["Name"], tile["Desc"], tile["Blocked"],
                         tile["Character"], tile["Color"], game_entities_)

        self.game_data: databases.Databases = game_data
        self.game_interface: interface.Interface = game_interface

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
        self.game_interface.message_box.add_msg(
            f"Alarms sounded.", self.game_data.colors["SYS_MSG"]
        )

    # What happens when successfully hacked.
    def _success_hack(self, actor_: "actor.Actor") -> None:
        self.game_interface.message_box.add_msg(
            f"{actor_.name} successfully hacks the terminal.", self.game_data.colors["SUCCESS_MSG"]
        )

        for result in self.success_results:
            if result == self.SuccessResult.UNLOCK_DOORS:
                self._unlock_doors()

    # What happens when unsuccessfully hacked.
    def _fail_hack(self, actor_: "actor.Actor") -> None:
        self.game_interface.message_box.add_msg(
            f"{actor_.name} fails to hack the terminal.", self.game_data.colors["BAD_MSG"]
        )

        for result in self.fail_results:
            if result == self.FailResult.SOUND_ALARM:
                self._sound_alarm()

    # Called by an actor that wants to attempt to hack the terminal.
    def attempt_hack(self, actor_: "actor.Actor") -> None:
        if actor_.hacking_skill > self.difficulty:
            self._success_hack(actor_)
        else:
            self._fail_hack(actor_)
