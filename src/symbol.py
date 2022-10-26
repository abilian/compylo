class Symbol:
    def __init__(self, name, typ=None):
        self.name: str = name
        self.type = typ

    def __str__(self):
        return f"{self.name}: {self.type}"

    def __eq__(self, other):
        if other is None:
            return False

        return self.type == other.type and self.name == other.name
