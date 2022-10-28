class UnknownTypeError(Exception):
    def __init__(self, typ, message=None):
        self.typ = typ
        if message is None:
            self.message = f"Unknown type: {self.typ}"
        else:
            self.message = message


class IncompatibleTypeError(Exception):
    def __init__(self, t1, t2, message=None):
        self.t1 = t1
        self.t2 = t2
        if message is None:
            self.message = (
                f"Operation between incompatile types: {t1} and {t2}"
            )
        else:
            self.message = message
