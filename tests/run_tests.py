import yaml
import subprocess
from utils import *
from typing import List
import termcolor as tc

OK_LABEL = tc.colored("[ OK ]".ljust(12, " "), "green")
KO_LABEL = tc.colored("[ KO ]".ljust(12, " "), "red")


def getTestList(filePath: str):
    res = []
    with open(filePath) as f:
        content = f.read()
        data = yaml.load_all(content, yaml.Loader)
        for d in data:
            res.append(d)

    return res


def runTest(test: YamlTestCase) -> bool:
    """
    @brief      Runs a single test and compares its exit_code to the
                expected one
    @param      test    utils.YamlTestCase object representing the case to be ran
    """
    args = test.command.split(" ")
    process = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    ret = process.wait()

    return ret == test.exit_code


def runTests(testList: List[YamlTestCase]):
    """
    @brief              Returns the list of all successful tests
    @param  testList    The list of tests to be ran
    """

    def run(t):
        print(t.name.ljust(48, " "), end="")
        if runTest(t):
            print(OK_LABEL.ljust(16, " "), end="")
            print(tc.colored(f"-> {t.file}", "cyan"))
            return True

        print(KO_LABEL.ljust(16, " "), end="")
        print(tc.colored(f"-> {t.file}", "cyan"))
        return False

    return sum(map(run, testList))


if __name__ == "__main__":
    passed = 0
    failed = 0
    total = 0

    for d in DIRECTORIES:
        testList = getTestList(f"{d}.yaml")
        total += len(testList)
        successfulTests = runTests(testList)
        passed += successfulTests
        failed += len(testList) - successfulTests

    passed_message = tc.colored(f"PASSED: {passed}", "green")
    failed_message = tc.colored(f"FAILED: {failed}", "red")
    total_message = tc.colored(f"TOTAL: {total}", "blue")

    print()
    print(passed_message)
    print(failed_message)
    print(total_message)
