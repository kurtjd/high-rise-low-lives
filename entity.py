class Entity:
    # ~~~ STATIC METHODS ~~~

    def __init__(self, x, y, name, desc, blocked, graphic, color, game_entities):
        self.x = x
        self.y = y
        self.name = name
        self.desc = desc
        self.graphic = graphic
        self.color = color
        self.bgcolor = None
        self.blocked = blocked
        self.game_entities = game_entities
        game_entities.all.append(self)

    # ~~~ PUBLIC METHODS ~~~

    # Draws a game entity to the screen
    def render(self, console):
        console.print(x=self.x, y=self.y, string=self.graphic, fg=self.color, bg=self.bgcolor)

    def update(self, game_time):
        pass

    def remove(self):
        for entity in enumerate(self.game_entities.all):
            if entity[1] is self:
                self.game_entities.all.pop(entity[0])
