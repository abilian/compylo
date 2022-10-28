from typeVisitor import TypeVisitor
from binder import Binder
from renamer import Renamer
import sys
import ast


def main():
    if len(sys.argv) != 2:
        print("USAGE: python ./compylo.py FILE")
        return 1

    file = sys.argv[1]
    content = ""
    with open(file) as f:
        content = f.read()

    root = ast.parse(content)

    Binder()(root)
    Renamer()(root)
    TypeVisitor()(root)

    return 0


if __name__ == "__main__":
    main()
