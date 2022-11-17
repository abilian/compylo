import pathlib
import sys
import yaml

from typing import List
from os.path import isfile, join
from os import listdir
from .utils import *


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


def generateTestCase(filePath: pathlib.PosixPath):
    """
    @brief              Generates the yaml for 1 test
    @param filePath     path of the file to the script against
    """
    assert filePath.suffix == ".py"
    file = str(filePath)
    name = filePath.stem

    (args, exit_code) = __get_args(filePath)

    return YamlTestCase(name, args, file, exit_code)


def generateYaml(filename: str, tests: List[str]):
    """
    @brief              Generates a Yaml file for tests
    @param filename     The name of the file to generate
    @param tests        A list of the files to test from this yaml
    """
    with open(filename, "w+") as f:
        f.write(
            yaml.dump_all(
                list(
                    map(
                        lambda t: generateTestCase(pathlib.PosixPath(t)), tests
                    )
                )
            )
        )


if __name__ == "__main__":
    for d in DIRECTORIES:
        testFiles = [join(d, f) for f in listdir(d) if isfile(join(d, f))]
        yamlFile = f"{d}.yaml"
        generateYaml(yamlFile, testFiles)
