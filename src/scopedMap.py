class ScopedMap:
    """
    Map holding a list of (str, dict) representing successive scopes of the
    program. The dict is filled with combos `name: symbol`
    """

    def __init__(self):
        self.symbols = [("global", {})]
        self.current = 0

    def __str__(self):
        s = "ScopedMap {\n"
        indent = 1
        for (name, content) in self.symbols:
            s += indent * "\t"
            s += f"{name}:\n"
            indent += 1
            for c in content:
                s += indent * "\t"
                s += f"{str(content[c])}\n"
            indent -= 1
            s += "\n"
        s += "}"

        return s

    def push_scope(self, name):
        """
        Adds a new empty scope into the map
        """
        self.symbols.append((name, {}))
        self.current += 1

    def pop_scope(self):
        """
        Removes the last scope
        """
        if self.current > 0:
            self.current -= 1

    def append(self, sym):
        """
        Adds a symbol into the current scope
        """
        dic = self.symbols[-1][1]
        dic[sym.name] = sym

    def update(self, sym):
        s = self.find(sym.name)
        if s == None:
            self.append(sym)
        else:
            s.type = sym

    def find(self, symName):
        """
        Finds a symbol with a given name in the table.
        Returns None if not found
        """

        for t in self.symbols:
            if symName in t[1]:
                return t[1][symName]

        return None

    def contains(self, sym):
        """
        Checks if a symbol exists in a table, using find
        """
        return self.find(sym) != None
