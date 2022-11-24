from .singleton import Singleton


class Int(metaclass=Singleton):
    """
    @brief  Class for int type
    """

    def compatible_with(self, other):
        return other == self


class Float(metaclass=Singleton):
    """
    @brief  Class for float type
    """

    def compatible_with(self, other):
        return other == self


class Bool(metaclass=Singleton):
    """
    @brief  Class for bool type
    """

    def compatible_with(self, other):
        return other == self


class String(metaclass=Singleton):
    """
    @bref   Class for String type
    """

    def compatible_with(self, other):
        return other == self
