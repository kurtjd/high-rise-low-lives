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

        def render(self, console: tcod.Console, wieldables: dict) -> None:
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

            for wieldable in enumerate(wieldables):
                # For smoother grammar
                amount: Union[int, str] = wieldable[1]["Amount"]
                if amount == 1:
                    amount = 'a'

                console.print(
                    x=self.x,
                    y=self.y + 2 + wieldable[0],
                    string=f"{wieldable[1]['ID']} - {amount} {wieldable[1]['Item'].name}",
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

            for item in enumerate(actor_.inventory):
                # For smoother grammar
                amount: Union[int, str] = item[1]["Amount"]
                if amount == 1:
                    amount = 'a'

                console.print(
                    0,
                    1 + item[0],
                    string=f"{item[1]['ID']} - {amount} {item[1]['Item'].name}",
                    fg=tcod.cyan
                )

    class ThrowScreen:
        def __init__(self, x: int, y: int) -> None:
            self.x: int = x
            self.y: int = y

        def render(self, console: tcod.Console, actor_: "entities.Actor") -> None:
            console.print(
                self.x,
                self.y,
                string=f"Throw which item?",
                fg=tcod.green
            )

            for item in enumerate(actor_.inventory):
                if item[1]["Item"].throwable:
                    # For smoother grammar
                    amount: Union[int, str] = item[1]["Amount"]
                    if amount == 1:
                        amount = 'a'

                    console.print(
                        0,
                        1 + item[0],
                        string=f"{item[1]['ID']} - {amount} {item[1]['Item'].name}",
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
            self.actor: Optional["entities.Actor"] = None

            self.floor: int = 1
            self.time: int = 0

        # ~~~ PUBLIC METHODS ~~~

        # Sets the actor whos stats we want to show up.
        def set_actor(self, actor_: "entities.Actor") -> None:
            self.actor: "entities.Actor" = actor_

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
                string=f"{self.actor.name}\nThe {self.actor.race} {self.actor.class_name}",
                fg=tcod.cyan,
            )

            # Show stats
            console.print(
                x=self.x + 2,
                y=self.y + 5,
                string=(
                    f"HP: {self.actor.health}        MP: {self.actor.mp}\n"
                    f"Charge: {self.actor.charge}%    AC: {self.actor.ac}"
                ),
                fg=tcod.purple
            )

            # Show attributes
            console.print(
                x=self.x + 2,
                y=self.y + 10,
                string=(
                    f"Muscle: {self.actor.muscle}     Smarts: {self.actor.smarts}\n"
                    f"Reflexes: {self.actor.reflexes}   Charm: {self.actor.charm}\n"
                    f"Grit: {self.actor.grit}       Wits: {self.actor.wits}"
                ),
                fg=tcod.pink
            )

            # Show worn
            console.print(
                x=self.x + 2,
                y=self.y + 16,
                string=f"Wielding: {self.actor.wielding}\nWearing: {self.actor.wearing}",
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
