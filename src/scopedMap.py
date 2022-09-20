class ScopedMap:
    """
        Map holding a list of (str, dict) representing successive scopes of the
        program. The dict is filled with combos `name: symbol`
    """
    def __init__(self):
        self.symbols = [('global', {})]

    def push_scope(self, name):
        """
            Adds a new empty scope into the map
        """
        self.symbols.append((name, {}))

    def pop_scope(self):
        """
            Removes the last scope
        """
        if (len(self.symbols) > 0):
            self.symbols.pop()

    def append(self, sym):
        """
            Adds a symbol into the last scope
        """
        dic = self.symbols[-1][1]
        dic[sym.name] = sym

    def find(self, sym):
        """
            Finds a symbol in the table.
            Returns None if not found
        """

        for t in self.symbols:
            if sym.name in t[1]:
                return t[1][sym.name]

        return None

    def contains(self, sym):
        """
            Checks if a symbol exists in a table, using find
        """
        return self.find(sym) != None
