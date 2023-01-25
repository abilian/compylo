# FIXME: this tests will fail until the main() scope is introduced
x: int = 1

def f(a: int) -> int:
    y = x + a
    return y
