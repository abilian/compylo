from symbol import *
from typing import List, Dict

class ScopedMap:
    """
    Map holding a list of (str, dict) representing successive scopes of the
    program. The dict is filled with combos `name: symbol`
    """

    def __init__(self):
        self.symbols: Dict[str, List[Symbol]] = {"global": []}
        self.current: str = "global"
        self.old: List[str] = []

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

    def append(self, sym):
        """
        Adds a symbol into the current scope
        """
        self.symbols[self.current].append(sym)

    def remove(self, sym):
        self.symbols[self.current].remove(sym)

    def update(self, sym: Symbol):
        s = self.find(sym.name)
        if s == None:
            self.append(sym)
            return False

        s.type = sym.type
        return True

    def find(self, symName: str, current=True):
        """
        Finds a symbol with a given name in the table.
        Returns None if not found
        """
        toSearch: List[str] = [self.current] # Scopes where the variable can be found
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
