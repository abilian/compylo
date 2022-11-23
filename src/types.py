from .singleton import Singleton


class Int(metaclass=Singleton):
    """
    @brief  Class for int type
    """

    def compatible_with(self, other):
        return isinstance(other, Int)


class Float(metaclass=Singleton):
    """
    @brief  Class for float type
    """

    def compatible_with(self, other):
        return isinstance(other, Float)


class Bool(metaclass=Singleton):
    """
    @brief  Class for bool type
    """

    def compatible_with(self, other):
        return isinstance(other, Bool)
