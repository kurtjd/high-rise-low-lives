import tcod
import globals


# ~~~ STATIC METHODS ~~~

# Called by anything that wants to send a message to the message box.
def send_msg(msg_box, message, color):
    msg_box.add_msg(message, color)


class HUD:
    # ~~~ PRIVATE METHODS ~~~

    def __init__(self, x, y, width, height):
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
            fg=tcod.cyan
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


class Messages:
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


def render_inventory_screen(inventory, console):
    console.print(
        0,
        0,
        string=f"Inventory: {len(inventory)} / {globals.MAX_INVENTORY_SIZE} slots",
        fg=tcod.green
    )

    for item in enumerate(inventory):
        # For smoother grammar
        amount = item[1]['Amount']
        if amount == 1:
            amount = 'a'

        console.print(
            0,
            1 + item[0],
            string=f"{item[1]['ID']} - {amount} {item[1]['Item'].name}",
            fg=tcod.cyan
        )
