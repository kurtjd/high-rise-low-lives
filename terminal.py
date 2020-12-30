import entity
from enum import Enum, auto


# Terminals can be hacked to do things like:
# open doors, turn off security cameras, disable turrets and traps, download programs, etc
# If failed to hack, can do nasty things like sound an alarm, explode, give you a virus, etc
class Terminal(entity.Entity):
    class SuccessResult(Enum):
        DISABLE_CAMS = auto(),
        DISABLE_TURRETS = auto(),
        UNLOCK_DOORS = auto()

    class FailResult(Enum):
        SOUND_ALARM = auto(),
        EXPLODE = auto()

    def __init__(self, x, y, game_data, game_entities, game_interface):
        tile = game_data.tiles["TERMINAL"]
        super().__init__(x, y, tile["Name"], tile["Desc"], tile["Blocked"],
                         tile["Character"], tile["Color"], game_entities)

        self.game_data = game_data
        self.game_interface = game_interface

        self.difficulty = 0
        self.success_results = []
        self.fail_results = []
        self._choose_results()

        game_entities.terminals.append(self)

    # This will decide randomly which and how many success/fail results to generate for this terminal.
    # The number of success will increase difficulty and the higher the difficulty the more number of fails.
    def _choose_results(self):
        self.success_results.append(self.SuccessResult.UNLOCK_DOORS)
        self.fail_results.append(self.FailResult.SOUND_ALARM)
        self.difficulty = 5

    def _unlock_doors(self):
        for door in self.game_entities.doors:
            door.locked = False

        self.game_interface.message_box.add_msg(
            f"All doors unlocked.", self.game_data.colors["SYS_MSG"]
        )

    def _sound_alarm(self):
        self.game_interface.message_box.add_msg(
            f"Alarms sounded.", self.game_data.colors["SYS_MSG"]
        )

    # What happens when successfully hacked.
    def _success_hack(self, actor):
        self.game_interface.message_box.add_msg(
            f"{actor.name} successfully hacks the terminal.", self.game_data.colors["SUCCESS_MSG"]
        )

        for result in self.success_results:
            if result == self.SuccessResult.UNLOCK_DOORS:
                self._unlock_doors()

    # What happens when unsuccessfully hacked.
    def _fail_hack(self, actor):
        self.game_interface.message_box.add_msg(
            f"{actor.name} fails to hack the terminal.", self.game_data.colors["BAD_MSG"]
        )

        for result in self.fail_results:
            if result == self.FailResult.SOUND_ALARM:
                self._sound_alarm()

    # Called by an actor that wants to attempt to hack the terminal.
    def attempt_hack(self, actor):
        if actor.hacking_skill > self.difficulty:
            self._success_hack(actor)
        else:
            self._fail_hack(actor)
