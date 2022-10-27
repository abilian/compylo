class Symbol:
    def __init__(self, name, typ=None, definition=None):
        self.name: str = name
        self.type = typ
        self.definition = definition # The node where the symbol was defined

    def __str__(self):
        if self.definition is not None:
            return f"{self.name}: {self.type}. defined by {self.definition}"
        return f"{self.name}: {self.type}"

    def __eq__(self, other):
        if other is None or type(other) != type(self):
            return False

        return self.type == other.type and self.name == other.name
