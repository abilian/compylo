from os.path import isfile, join
from os import listdir
import pathlib
import sys
from typing import List

PATH = "src/"
DEFAULT_ARGS = "-T"
DIRECTORIES = ["good", "bind", "type"]


class YamlTestCase:
    def __init__(self, name: str, args: str, file: str, exit_code: int):
        self.args = args
        self.name = name
        self.file = file
        self.exit = exit_code
        self.command = f"{PATH} {self.args} {self.file}"

    def __repr__(self):
        return f"""test:
    - name: {self.name}
    - file: {self.file}
    - exit_code: {self.exit}
    - command: {self.command}

"""


def __get_args(filePath: pathlib.PosixPath):
    match filePath.parent.name:
        case "good":
            return (DEFAULT_ARGS, 0)
        case "bind":
            return ("-B", 2)
        case "type":
            return ("-T", 3)
        case _:
            sys.exit(f"{filePath} not in the right place !")


"""
    @brief              Generates the yaml for 1 test
    @param filePath     path of the file to the script against
"""


def generateTestCase(filePath: pathlib.PosixPath):
    assert filePath.suffix == ".py"
    file = str(filePath)
    name = filePath.stem

    (args, exit_code) = __get_args(filePath)

    return YamlTestCase(name, args, file, exit_code)


"""
    @brief              Generates a Yaml file for tests
    @param filename     The name of the file to generate
    @param tests        A list of the files to test from this yaml
"""


def generateYaml(filename: str, tests: List[str]):
    with open(filename, "w+") as f:
        for testFiles in tests:
            path = pathlib.PosixPath(testFiles)
            print(f"path: {path}")
            case = generateTestCase(path)
            f.write(str(case))


if __name__ == "__main__":
    for d in DIRECTORIES:
        testFiles = [join(d, f) for f in listdir(d) if isfile(join(d, f))]
        yamlFile = f"{d}.yaml"
        generateYaml(yamlFile, testFiles)
