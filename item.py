class Item:
    # ~~~ PRIVATE METHODS ~~~

    def __init__(self, name, desc, use_action=None):
        self.name = name
        self.desc = desc
        self.use_action = use_action
