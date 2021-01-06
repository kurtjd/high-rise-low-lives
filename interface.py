from typing import Optional, Union, Any
import tcod
import entities


class Interface:
    def __init__(self, screen_w: int, screen_h: int, map_w: int, map_h: int) -> None:
        self.screen_w: int = screen_w
        self.screen_h: int = screen_h
        self.map_w: int = map_w
        self.map_h: int = map_h

        self.wield_screen: Interface.WieldScreen = self.WieldScreen(0, 0)
        self.description_screen: Interface.DescriptionScreen = self.DescriptionScreen(0, 0)
        self.inventory_screen: Interface.InventoryScreen = self.InventoryScreen(0, 0)
        self.throw_screen: Interface.ThrowScreen = self.ThrowScreen(0, 0)
        self.drug_screen: Interface.DrugScreen = self.DrugScreen(0, 0)
        self.charge_screen: Interface.ChargeScreen = self.ChargeScreen(0, 0)

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

    class WieldScreen:
        def __init__(self, x: int, y: int) -> None:
            self.x: int = x
            self.y: int = y

        def render(self, console: tcod.Console, wieldables: list) -> None:
            console.print(
                x=self.x,
                y=self.y,
                string="Wield which weapon?",
                fg=tcod.green
            )
            console.print(
                x=self.x,
                y=self.y + 1,
                string="- unarmed",
                fg=tcod.white
            )

            wieldables.sort()
            for wieldable in enumerate(wieldables):
                # For smoother grammar
                amount: Union[int, str] = wieldable[1][1]["Amount"]
                if amount == 1:
                    amount = 'a'

                console.print(
                    x=self.x,
                    y=self.y + 2 + wieldable[0],
                    string=f"{wieldable[1][0]} - {amount} {wieldable[1][1]['Item'].name}",
                    fg=tcod.cyan
                )

    class DescriptionScreen:
        def __init__(self, x: int, y: int) -> None:
            self.x: int = x
            self.y: int = y

        def render(self, console: tcod.Console, thing: Any) -> None:
            console.print(
                x=self.x,
                y=self.y,
                string=f"{thing.name}",
                fg=tcod.green
            )
            console.print(
                x=self.x,
                y=self.y + 2,
                string=f"{thing.desc}",
                fg=tcod.white
            )

    class InventoryScreen:
        def __init__(self, x: int, y: int) -> None:
            self.x: int = x
            self.y: int = y

        def render(self, console: tcod.Console, actor_: "entities.Actor") -> None:
            console.print(
                self.x,
                self.y,
                string=f"Inventory: {len(actor_.inventory)} / {actor_.MAX_INVENTORY_SIZE} slots",
                fg=tcod.green
            )

            items: list = [item_ for item_ in actor_.inventory.items()]
            items.sort()
            for item in enumerate(items):
                # For smoother grammar
                amount: Union[int, str] = item[1][1]["Amount"]
                if amount == 1:
                    amount = 'a'

                console.print(
                    0,
                    1 + item[0],
                    string=f"{item[1][0]} - {amount} {item[1][1]['Item'].name}",
                    fg=tcod.cyan
                )

    class ThrowScreen:
        def __init__(self, x: int, y: int) -> None:
            self.x: int = x
            self.y: int = y

        def render(self, console: tcod.Console, throwables: list) -> None:
            console.print(
                x=self.x,
                y=self.y,
                string="Throw which item?",
                fg=tcod.green
            )

            throwables.sort()
            for throwable in enumerate(throwables):
                # For smoother grammar
                amount: Union[int, str] = throwable[1][1]["Amount"]
                if amount == 1:
                    amount = 'a'

                console.print(
                    x=self.x,
                    y=self.y + 2 + throwable[0],
                    string=f"{throwable[1][0]} - {amount} {throwable[1][1]['Item'].name}",
                    fg=tcod.cyan
                )

    class DrugScreen:
        def __init__(self, x: int, y: int) -> None:
            self.x: int = x
            self.y: int = y

        def render(self, console: tcod.Console, drugs: list) -> None:
            console.print(
                self.x,
                self.y,
                string=f"Use which drug?",
                fg=tcod.green
            )

            drugs.sort()
            for drug in enumerate(drugs):
                # For smoother grammar
                amount: Union[int, str] = drug[1][1]["Amount"]
                if amount == 1:
                    amount = 'a'

                console.print(
                    0,
                    1 + drug[0],
                    string=f"{drug[1][0]} - {amount} {drug[1][1]['Item'].name}",
                    fg=tcod.cyan
                )

    class ChargeScreen:
        def __init__(self, x: int, y: int) -> None:
            self.x: int = x
            self.y: int = y

        def render(self, console: tcod.Console, power_sources: list) -> None:
            console.print(
                self.x,
                self.y,
                string=f"Charge with which power-source?",
                fg=tcod.green
            )

            power_sources.sort()
            for powersrc in enumerate(power_sources):
                # For smoother grammar
                amount: Union[int, str] = powersrc[1][1]["Amount"]
                if amount == 1:
                    amount = 'a'

                console.print(
                    0,
                    1 + powersrc[0],
                    string=f"{powersrc[1][0]} - {amount} {powersrc[1][1]['Item'].name}",
                    fg=tcod.cyan
                )

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

        def render(self, console: tcod.Console) -> None:
            # Makes little barrier
            for i in range(self.height):
                console.print(x=self.x, y=self.y+i, string=chr(9474), fg=tcod.green)

            # Shows who you are
            console.print(
                x=self.x+2,
                y=self.y+1,
                string=f"{self.player.name}\nThe {self.player.race} {self.player.class_name}",
                fg=tcod.cyan,
            )

            # Show stats
            console.print(
                x=self.x + 2,
                y=self.y + 5,
                string=(
                    f"HP: {self.player.health}        MP: {self.player.mp}\n"
                    f"Charge: {self.player.charge_percent}%    AC: {self.player.ac}"
                ),
                fg=tcod.purple
            )

            # Show attributes
            console.print(
                x=self.x + 2,
                y=self.y + 10,
                string=(
                    f"Muscle: {self.player.muscle}     Smarts: {self.player.smarts}\n"
                    f"Reflexes: {self.player.reflexes}   Charm: {self.player.charm}\n"
                    f"Grit: {self.player.grit}       Wits: {self.player.wits}"
                ),
                fg=tcod.pink
            )

            # Show worn
            console.print(
                x=self.x + 2,
                y=self.y + 16,
                string=f"Wielding: {self.player.wielding}\nWearing: {self.player.wearing}",
                fg=tcod.white
            )

            # Show game stats
            console.print(
                x=self.x + 2,
                y=self.y + 21,
                string=f"Floor: {self.floor}       Time: {self.time}",
                fg=tcod.flame
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
        def render(self, console: tcod.Console) -> None:
            # Makes little barrier
            for i in range(self.width):
                console.print(x=self.x + i, y=self.y, string=chr(9472), fg=tcod.green)

            for msg in enumerate(self.messages):
                console.print(
                    x=self.x + 1,
                    y=self.y + 1 + msg[0],
                    string=f"> {msg[1]['Text']}",
                    fg=msg[1]['Color']
                )
