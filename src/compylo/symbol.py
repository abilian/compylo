class Symbol:
    def __init__(self, name, definition=None):
        self.name: str = name
        self.definition = definition  # The node where the symbol was defined

    def __str__(self):
        if self.definition is not None:
            return f"{self.name}: defined by {self.definition}"
        return f"{self.name}"

    def __eq__(self, other):
        if other is None or type(other) != type(self):
            return False

        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
