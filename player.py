import actor


# This is a small class since the player mostly shares characteristics with other actors except a few things.

class Player(actor.Actor):
    def __init__(self, name, race, class_name, desc, x, y, health, muscle, smarts, reflexes, wits, grit,
                 graphic, color, game_data, game_entities, game_interface):
        super().__init__(name, race, class_name, desc, x, y, health, muscle, smarts, reflexes, wits, grit,
                         None, True, graphic, color, game_data, game_entities, game_interface)
        self.examine_target = None
