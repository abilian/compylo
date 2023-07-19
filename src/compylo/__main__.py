import argparse
import ast
import sys
import traceback

from .binder import Binder
from .desugar import DesugarVisitor
from .errors import BindError, TypeCheckError
from .printer import Printer
from .renamer import Renamer
from .translator import Translator
from .type_checker import TypeChecker
from .type_inference import TypeInference


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
    group.add_argument(
        "-D", "--desugar", help="desugars the ast", action="store_true"
    )
    group.add_argument(
        "-L",
        "--llvm-compute",
        help="creates a .ll file with the llvm IR corresponding",
        action="store_true",
    )

    return parser


def get_action(action: str):
    action_map = {
        "print": Printer,
        "bind": Binder,
        "rename": Renamer,
        "infer": TypeInference,
        "type": TypeChecker,
        "desugar": DesugarVisitor,
        "llvm-compute": Translator,
    }

    return action_map[action]


def dependencies(action: str, node: ast.AST):
    dependencies_map = {
        "print": None,
        "bind": None,
        "rename": "bind",
        "infer": "rename",
        "type": "infer",
        "desugar": "type",
        "llvm-compute": "desugar",
    }

    if not dependencies_map[action]:
        return get_action(action)()(node)

    dependencies(dependencies_map[action], node)

    return get_action(action)()(node)


def arg_action(args: argparse.Namespace):
    if args.rename:
        return "rename"
    if args.bind:
        return "bind"
    if args.infer:
        return "infer"
    if args.type:
        return "type"
    if args.desugar:
        return "desugar"

    return "llvm-compute"


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
