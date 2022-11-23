from .typeInference import TypeInference
from .typeChecker import TypeChecker
from .printer import Printer
from .binder import Binder
from .renamer import Renamer
from .errors import *
import argparse
import sys, ast, traceback


def setup_parser():
    parser = argparse.ArgumentParser(
        prog="compylo",
        description="Python\
                                     to WASM Compiler using LLVVM",
    )

    parser.add_argument("FILENAME", help="the file to compile")
    parser.add_argument(
        "-P", "--print", help="print the processed ast", action="store_true"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-B", "--bind", help="bind the ast", action="store_true"
    )
    group.add_argument(
        "-R", "--rename", help="rename the variables", action="store_true"
    )
    group.add_argument(
        "-I", "--infer", help="infer types", action="store_true"
    )
    group.add_argument(
        "-T", "--type", help="compute types", action="store_true"
    )

    return parser


def get_action(action: str):
    actionMap = {
        "print": Printer(),
        "bind": Binder(),
        "rename": Renamer(),
        "infer": TypeInference(),
        "type": TypeChecker(),
    }

    return actionMap[action]


def dependencies(action: str, node: ast.AST):
    dependenciesMap = {
        "print": [],
        "bind": [],
        "rename": ["bind"],
        "infer": ["rename"],
        "type": ["infer"],
    }

    if not dependenciesMap[action]:
        return get_action(action)(node)

    dependencies(dependenciesMap[action][0], node)
    # FIXME: with this approach, flags can only have 1 dep

    return get_action(action)(node)


def arg_action(args: argparse.Namespace):
    if args.rename:
        return "rename"
    if args.bind:
        return "bind"
    if args.infer:
        return "infer"

    return "type"


def main():
    parser = setup_parser()
    args = parser.parse_args()
    file = args.FILENAME

    with open(file) as f:
        content = f.read()

    root = ast.parse(content)

    try:
        action = arg_action(args)
        dependencies(action, root)
        if args.print:
            Printer()(root)
    except BindError as e:
        traceback.print_exception(e)
        sys.exit(2)
    except TypeCheckError as e:
        traceback.print_exception(e)
        sys.exit(3)

    return 0


if __name__ == "__main__":
    main()
