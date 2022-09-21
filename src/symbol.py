class Symbol:
    counter = 0

    def __init__(self, name=None):
        self.type = None
        if (name is None):
            self.name = 'tmp__{self.counter}'
            Symbol.counter += 1
        else:
            self.name = name

    def __str__(self):
        return f'{self.name} : {self.type}'

    def __eq__(self, other):
        return self.type == other and self.name == other.name
