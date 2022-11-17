from .run_tests import *
from .binder_tests import *

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
