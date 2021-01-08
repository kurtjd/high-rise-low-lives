from typing import Optional, Union, Any
import rendering
import entities


class Interface:
    def __init__(self, screen_w: int, screen_h: int, map_w: int, map_h: int) -> None:
        self.screen_w: int = screen_w
        self.screen_h: int = screen_h
        self.map_w: int = map_w
        self.map_h: int = map_h

        self.wield_screen: Interface.WieldScreen = self.WieldScreen()
        self.description_screen: Interface.DescriptionScreen = self.DescriptionScreen()
        self.inventory_screen: Interface.InventoryScreen = self.InventoryScreen()
        self.throw_screen: Interface.ThrowScreen = self.ThrowScreen()
        self.drug_screen: Interface.DrugScreen = self.DrugScreen()
        self.charge_screen: Interface.ChargeScreen = self.ChargeScreen()

        self.stats_box: Interface.StatsBox = self.StatsBox(
            self.map_w + 1,
            0,
            self.screen_w - self.map_w,
            self.screen_h
        )
        self.message_box: Interface.MessageBox = self.MessageBox(
            0,
            self.map_h,
            self.map_w + 1,
            self.screen_h - self.map_h
        )

    class DescriptionScreen:
        def __init__(self, x: int = 0, y: int = 0) -> None:
            self.x: int = x
            self.y: int = y

        def render(self, surface: Any, thing: Any) -> None:
            rendering.render(surface, thing.name, self.x, self.y, (0, 255, 0))
            rendering.render(surface, thing.desc, self.x, self.y + 2, (255, 255, 255))

    class SelectScreen:
        def __init__(self, x: int = 0, y: int = 0) -> None:
            self.x: int = x
            self.y: int = y

        def print_items(self, items: list[tuple[str, dict]], surface: Any):
            items.sort()
            for item in enumerate(items):
                # For smoother grammar
                amount: Union[int, str] = item[1][1]["Amount"]
                if amount == 1:
                    amount = 'a'

                rendering.render(
                    surface,
                    f"{item[1][0]} - {amount} {item[1][1]['Item'].name}",
                    self.x,
                    self.y + 2 + item[0],
                    (0, 255, 255)
                )

    class WieldScreen(SelectScreen):
        def __init__(self, x: int = 0, y: int = 0) -> None:
            super().__init__(x, y)

        def render(self, surface: Any, wieldables: list[tuple[str, dict]]) -> None:
            rendering.render(
                surface,
                "Wield which weapon?",
                self.x,
                self.y,
                (0, 255, 0)
            )
            rendering.render(
                surface,
                "- unarmed",
                self.x,
                self.y + 1,
                (255, 255, 255)
            )

            self.print_items(wieldables, surface)

    class InventoryScreen(SelectScreen):
        def __init__(self, x: int = 0, y: int = 0) -> None:
            super().__init__(x, y)

        def render(self, surface: Any, actor_: "entities.Actor") -> None:
            rendering.render(
                surface,
                f"Inventory: {len(actor_.inventory)} / {actor_.MAX_INVENTORY_SIZE} slots",
                self.x,
                self.y,
                (0, 255, 0)
            )

            items: list[tuple[str, dict]] = [item_ for item_ in actor_.inventory.items()]
            self.print_items(items, surface)

    class ThrowScreen(SelectScreen):
        def __init__(self, x: int = 0, y: int = 0) -> None:
            super().__init__(x, y)

        def render(self, surface: Any, throwables: list[tuple[str, dict]]) -> None:
            rendering.render(
                surface,
                "Throw which item?",
                self.x,
                self.y,
                (0, 255, 0)
            )

            self.print_items(throwables, surface)

    class DrugScreen(SelectScreen):
        def __init__(self, x: int = 0, y: int = 0) -> None:
            super().__init__(x, y)

        def render(self, surface: Any, drugs: list[tuple[str, dict]]) -> None:
            rendering.render(
                surface,
                "Use which drug?",
                self.x,
                self.y,
                (0, 255, 0)
            )

            self.print_items(drugs, surface)

    class ChargeScreen(SelectScreen):
        def __init__(self, x: int = 0, y: int = 0) -> None:
            super().__init__(x, y)

        def render(self, surface: Any, power_sources: list[tuple[str, dict]]) -> None:
            rendering.render(
                surface,
                "Charge with which power-source?",
                self.x,
                self.y,
                (0, 255, 0)
            )

            self.print_items(power_sources, surface)

    class StatsBox:
        # ~~~ PRIVATE METHODS ~~~

        def __init__(self, x: int, y: int, width: int, height: int) -> None:
            self.x: int = x
            self.y: int = y
            self.width: int = width
            self.height: int = height

            # The actor whos stats appear here.
            self.player: Optional["entities.Player"] = None

            self.floor: int = 1
            self.time: int = 0

        # ~~~ PUBLIC METHODS ~~~

        # Sets reference to player.
        def set_actor(self, player_: "entities.Player") -> None:
            self.player: "entities.Player" = player_

        def update(self, time: int, floor: int) -> None:
            self.time: int = time
            self.floor: int = floor

        def render(self, surface: Any) -> None:
            # Makes little barrier
            for i in range(self.height):
                rendering.render(surface, chr(9474), self.x, self.y + i, (0, 255, 0))

            # Shows who you are
            rendering.render(
                surface,
                f"{self.player.name}\nThe {self.player.race} {self.player.class_name}",
                self.x + 2,
                self.y + 1,
                (0, 255, 255)
            )

            # Show stats
            rendering.render(
                surface,
                (
                    f"HP: {self.player.health}        MP: {self.player.mp}\n"
                    f"Charge: {self.player.charge_percent}%    AC: {self.player.ac}"
                ),
                self.x + 2,
                self.y + 5,
                (128, 0, 128)
            )

            # Show attributes
            rendering.render(
                surface,
                (
                    f"Muscle: {self.player.muscle}     Smarts: {self.player.smarts}\n"
                    f"Reflexes: {self.player.reflexes}   Charm: {self.player.charm}\n"
                    f"Grit: {self.player.grit}       Wits: {self.player.wits}"
                ),
                self.x + 2,
                self.y + 10,
                (255, 192, 203)
            )

            # Show worn
            wielding_: str
            if self.player.wielding is None:
                wielding_ = "Unarmed"
            else:
                wielding_ = self.player.wielding.name

                if self.player.wielding.distance == "RANGED":
                    rendering.render(
                        surface,
                        f"[{self.player.wielding.rounds_in_mag}/{self.player.wielding.mag_capacity}]",
                        self.x + 17,
                        self.y + 16,
                        (255, 255, 255)
                    )

            rendering.render(
                surface,
                f"Wielding: {wielding_}\nWearing: {self.player.wearing}",
                self.x + 2,
                self.y + 16,
                (255, 255, 255)
            )

            # Show currency
            rendering.render(
                surface,
                f"Smokes: {self.player.smokes}",
                self.x + 2,
                self.y + 18,
                (255, 215, 0)
            )

            # Show game stats
            rendering.render(
                surface,
                f"Floor: {self.floor}       Time: {self.time}",
                self.x + 2,
                self.y + 22,
                (255, 63, 0)
            )

    class MessageBox:
        # ~~~ PRIVATE METHODS ~~~

        def __init__(self, x: int, y: int, width: int, height: int) -> None:
            self.x: int = x
            self.y: int = y
            self.width: int = width
            self.height: int = height
            self.messages: list[dict] = []

        # ~~~ PUBLIC METHODS ~~~
        # Adds a message to the message box.
        def add_msg(self, msg: str, color: Optional[tuple[int, int, int]]) -> None:
            if len(self.messages) >= (self.height - 1):
                self.messages.pop(0)

            self.messages.append(dict({"Text": msg, "Color": color}))

        # Draws the messgae box to the screen.
        def render(self, surface: Any) -> None:
            # Makes little barrier
            for i in range(self.width):
                rendering.render(surface, chr(9472), self.x + i, self.y, (0, 255, 0))

            for msg in enumerate(self.messages):
                rendering.render(surface, f"> {msg[1]['Text']}", self.x + 1, self.y + 1 + msg[0], msg[1]['Color'])
