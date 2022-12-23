from .symbol import *
from typing import List, Dict


class ScopedMap:
    """
    Map holding a list of (str, dict) representing successive scopes of the
    program. The dict is filled with combos `name: symbol`
    """

    def __init__(self):
        self.symbols: Dict[Symbol, List[Symbol]] = {Symbol("global"): []}
        self.current: Symbol = Symbol("global")
        self.old: List[Symbol] = []

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
                s += f"{str(sym)}\n"
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

    def __move(self, old: List[Symbol], looking: str):
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
        if scope in list(
            map(lambda s: s.name, self.old)
        ):  # If we're going back to an 'old' scope
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
        toSearch: List[Symbol] = [
            self.current
        ]  # Scopes where the variable can be found
        if not current:
            toSearch += self.old

        for scope in toSearch:
            for symbol in self.symbols[scope]:
                if symbol.name == symName:
                    return symbol

        return None

    def contains(self, sym, current=False):
        """
        Checks if a symbol exists in a table, using find
        """
        return self.find(sym, current) != None
