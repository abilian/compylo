a: int = 1
b: int = 2

c: int = a + b
d: int = a - b
e: int = a * b

# NOT GOOD, should not pass typechecking
f: int = a / b
i: float = a // b

# TODO:
# g: int = a % b
# h = a ** b
