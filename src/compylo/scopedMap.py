from .symbol import Symbol


class ScopedMap:
    """
    Map holding a list of (str, dict) representing successive scopes of the
    program. The dict is filled with combos `name: symbol`
    """

    def __init__(self):
        self.symbols: dict[Symbol, list[Symbol]] = {Symbol("global"): []}
        self.current: Symbol = Symbol("global")
        self.old: list[Symbol] = []

    def __str__(self):
        """
        Prints using the following format:
        ScopedMap {
            scope1:
                symbol
                symbol

            scope2:
                symbol
                symbol
        }
        """
        s = "ScopedMap {\n"
        indent = 1

        for key in self.symbols:
            s += indent * "    "
            s += f"{key}:\n"
            indent += 1
            for sym in self.symbols[key]:
                s += indent * "    "
                s += f"{sym!s}\n"
            indent -= 1
            s += "\n"

        s += "}"

        return s

    def push_scope(self, name):
        """
        Adds a new empty scope into the map
        """
        self.old.append(self.current)
        self.symbols[name] = []
        self.current = name

    def pop_scope(self):
        """
        Removes the last scope
        """
        if self.old != []:
            self.current = self.old[-1]
            self.old.pop()

    def __move(self, old: list[Symbol], looking: str):
        for scope in self.symbols:
            for sym in self.symbols[scope]:
                if sym.name == looking:
                    self.__move(old, scope.name)
                    old.append(scope)

    def move_scope(self, scope: str):
        """
        Moves the 'current' scope to a given one, updating 'self.old' as if we
        were creating the scope.
        """
        if scope in [(s.name, self.old) for s in scope]:
            while self.old.pop().name != scope:
                continue
        else:
            old = []
            self.__move(old, scope)
            self.old = old

        self.current = Symbol(scope)

    def append(self, sym):
        """
        Adds a symbol into the current scope
        """
        if sym not in self.symbols[self.current]:
            self.symbols[self.current].append(sym)

    def remove(self, sym):
        self.symbols[self.current].remove(sym)

    def find(self, symName: str, current=True):
        """
        Finds a symbol with a given name in the table.
        Returns None if not found
        """
        to_search: list[Symbol] = [
            self.current
        ]  # Scopes where the variable can be found
        if not current:
            to_search += self.old

        for scope in to_search:
            for symbol in self.symbols[scope]:
                if symbol.name == symName:
                    return symbol

        return None

    def contains(self, sym, current=False):
        """
        Checks if a symbol exists in a table, using find
        """
        return self.find(sym, current) is not None
