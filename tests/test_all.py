import subprocess
from pathlib import Path

import pytest


def list_dir(dir):
    this_dir = Path(__file__).parent
    return [str(f) for f in (this_dir / dir).glob("*.py")]


@pytest.mark.parametrize("file", list_dir("good"))
def test_good(file):
    expected = 0
    ret = run_compiler(file)
    assert ret == expected


@pytest.mark.parametrize("file", list_dir("bind"))
def test_bind(file):
    expected = 2
    ret = run_compiler(file)
    assert ret == expected


@pytest.mark.parametrize("file", list_dir("type"))
def test_good(file):
    expected = 3
    ret = run_compiler(file)
    assert ret == expected


def run_compiler(file):
    cmd = f"python -m compylo -T {file}"
    args = cmd.split(" ")
    print(f"Running test: {cmd}")
    process = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    ret = process.wait()
    return ret
