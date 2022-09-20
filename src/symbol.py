class Symbol:
    counter = 0

    def __init__(self, name=None):
        self.type = None
        if (name is None):
            self.name = 'tmp'
        else:
            self.name = name
        self.name += f'__{self.counter}'
        Symbol.counter += 1

    def __str__(self):
        return f'{self.name} : {self.type}'

    def __eq__(self, other):
        return self.type == other and self.name == other.name
