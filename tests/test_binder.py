import ast
import subprocess
from pathlib import Path

import pytest

from compylo import binder


def list_dir(dir):
    this_dir = Path(__file__).parent
    return [str(f) for f in (this_dir / dir).glob("*.py")]


@pytest.mark.parametrize("file", list_dir("good"))
def test_binder_good(file):
    out = get_printer_output(file)
    root = ast.parse(out)
    binder.Binder()(root)
    # TODO: check that the binder worked


@pytest.mark.parametrize("file", list_dir("bind"))
def test_binder_bad(file):
    out = get_printer_output(file)
    root = ast.parse(out)
    binder.Binder()(root)
    # TODO: check that something failed


def get_printer_output(file):
    cmd = f"python -m compylo -T {file} -P"
    args = cmd.split(" ")
    print(f"Running test: {cmd}")
    process = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    (output, _) = process.communicate()
    return output
