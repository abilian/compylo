# FIXME: This test currently fails. Shadowing a variable and using the shadowed
# value at the same time is invalid
x: int = 1


def f(a: int) -> int:
    x = x + 1 # If it was `a = x + 1` this would be valid python.
    return a
