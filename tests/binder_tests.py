import ast
from .utils import *
from .run_tests import *
import termcolor as tc
from src import binder, errors  # XXX: ugly ??
import subprocess


def getPrinterOut(test: YamlTestCase):
    test.command += " -P"
    args = test.command.split(" ")
    process = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    (out, _) = process.communicate()

    return out


def testBinder():
    tests = getTestList("tests/good.yaml")
    passed = 0
    total = len(tests)
    printCategory("BINDER")

    def run(t):
        out = getPrinterOut(t)
        root = ast.parse(out)
        try:
            binder.Binder()(root)
            print(t.name.ljust(48, " "), end="")
            print(OK_LABEL.ljust(16, " "), end="")
            print(tc.colored(f"-> {t.file}", "cyan"))
            return True
        except errors.BindError:
            print(KO_LABEL.ljust(16, " "), end="")
            print(tc.colored(f"-> {t.file}", "cyan"))
            return False

    passed = runTests(tests, run)

    return (passed, total)


if __name__ == "__main__":
    testBinder()
