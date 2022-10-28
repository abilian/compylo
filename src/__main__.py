from typeVisitor import TypeVisitor
from binder import Binder
from renamer import Renamer
from errors import *
import sys, ast, traceback


def main():
    if len(sys.argv) != 2:
        print("USAGE: python ./compylo.py FILE")
        return 1

    file = sys.argv[1]
    content = ""
    with open(file) as f:
        content = f.read()

    root = ast.parse(content)

    try:
        Binder()(root)
        Renamer()(root)
        TypeVisitor()(root)
        TypeVisitor()(root)
    except UnknownSymbolError as e:
        traceback.print_exception(e)
        sys.exit(2)
    except UnknownTypeError or IncompatibleTypeError as e:
        traceback.print_exception(e)
        sys.exit(3)

    return 0


if __name__ == "__main__":
    main()
