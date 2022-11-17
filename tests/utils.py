import termcolor as tc

PATH = "src"
DEFAULT_ARGS = "-T"
DIRECTORIES = ["tests/good", "tests/bind", "tests/type"]


class YamlTestCase:
    def __init__(self, name: str, args: str, file: str, exit_code: int):
        self.args = args
        self.name = name
        self.file = file
        self.exit_code = exit_code
        self.command = f"python -m {PATH} {self.args} {self.file}"

    def __repr__(self):
        return f"""test:
    - name: {self.name}
    - file: {self.file}
    - exit_code: {self.exit_code}
    - command: {self.command}

"""


def printCategory(cat: str):
    print(
        tc.colored(
            f"\n\n==============      {cat}       ==============", "magenta"
        )
    )
