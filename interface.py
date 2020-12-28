import tcod
import globals


class Interface:
    def __init__(self):
        self.wield_screen = None
        self.description_screen = None
        self.inventory_screen = None
        self.stats_box = None
        self.message_box = None

    class WieldScreen:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def render(self, console, wieldables):
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
                amount = wieldable[1]["Amount"]
                if amount == 1:
                    amount = 'a'

                console.print(
                    x=self.x,
                    y=self.y + 2 + wieldable[0],
                    string=f"{wieldable[1]['ID']} - {amount} {wieldable[1]['Item'].name}",
                    fg=tcod.cyan
                )

    class DescriptionScreen:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def render(self, console, thing):
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
        def __init__(self, x, y, max_inventory_size):
            self.x = x
            self.y = y
            self.max_inventory_size = max_inventory_size

        def render(self, console, inventory):
            console.print(
                self.x,
                self.y,
                string=f"Inventory: {len(inventory)} / {self.max_inventory_size} slots",
                fg=tcod.green
            )

            for item in enumerate(inventory):
                # For smoother grammar
                amount = item[1]["Amount"]
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

        def __init__(self, x, y, width, height):
            # self.player = player
            self.x = x
            self.y = y
            self.width = width
            self.height = height

            self.name = "Hiro"
            self.race = "Human"
            self.class_name = "Infiltrator"
            self.hp = 100
            self.mp = 50
            self.charge = 100
            self.ac = 6
            self.muscle = 12
            self.reflexes = 20
            self.smarts = 12
            self.charm = 11
            self.grit = 111
            self.wits = 15
            self.wielding = None
            self.wearing = "Street Gi"
            self.floor = 1
            self.time = globals.time

        # ~~~ PUBLIC METHODS ~~~

        def update(self, hp, wielding, time):
            self.hp = hp
            self.time = time
            self.wielding = wielding

        def render(self, console):
            # Makes little barrier
            for i in range(self.height):
                console.print(x=self.x, y=self.y+i, string=chr(9474), fg=tcod.green)

            # Shows who you are
            console.print(
                x=self.x+2,
                y=self.y+1,
                string=f"{self.name}\nThe {self.race} {self.class_name}",
                fg=tcod.cyan,
            )

            # Show stats
            console.print(
                x=self.x + 2,
                y=self.y + 5,
                string=f"HP: {self.hp}        MP: {self.mp}\nCharge: {self.charge}%    AC: {self.ac}",
                fg=tcod.purple
            )

            # Show attributes
            console.print(
                x=self.x + 2,
                y=self.y + 9,
                string=f"""
Muscle: {self.muscle}       Smarts: {self.smarts}
Reflexes: {self.reflexes}     Charm: {self.charm}
Grit: {self.grit}         Wits: {self.wits}
    """,
                fg=tcod.pink
            )

            # Show worn
            console.print(
                x=self.x + 2,
                y=self.y + 16,
                string=f"Wielding: {self.wielding}\nWearing: {self.wearing}",
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

        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.messages = []

        # ~~~ PUBLIC METHODS ~~~
        # Adds a message to the message box.
        def add_msg(self, msg, color):
            if len(self.messages) >= (self.height - 1):
                self.messages.pop(0)

            self.messages.append(dict({"Text": msg, "Color": color}))

        # Draws the messgae box to the screen.
        def render(self, console):
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
