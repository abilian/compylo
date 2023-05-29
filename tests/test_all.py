from __future__ import annotations

import ast
from pathlib import Path

import pytest

from compylo.binder import Binder
from compylo.desugar import DesugarVisitor
from compylo.errors import TypeCheckError, UnknownSymbolError
from compylo.renamer import Renamer
from compylo.type_checker import TypeChecker
from compylo.type_inference import TypeInference


def list_dir(dir) -> list[Path]:
    this_dir = Path(__file__).parent
    paths = (this_dir / dir).glob("*.py")
    paths = filter(lambda path: not path.name.startswith("__"), paths)
    return list(paths)


@pytest.mark.parametrize("file", list_dir("good"))
def test_good(file):
    run_compiler(file)


@pytest.mark.parametrize("file", list_dir("bind"))
def test_bind(file):
    # Binding error
    # TODO: AtributeError should not happen
    with pytest.raises((UnknownSymbolError, AttributeError)):
        run_compiler(file)


@pytest.mark.parametrize("file", list_dir("type"))
def test_type(file):
    # Type error
    with pytest.raises(TypeCheckError):
        run_compiler(file)


def run_compiler(path):
    """Run the equivalent of `python -m compylo -T file`"""
    content = path.read_text()
    ast_root = ast.parse(content)
    Binder()(ast_root)
    Renamer()(ast_root)
    TypeInference()(ast_root)
    TypeChecker()(ast_root)
    DesugarVisitor()(ast_root)
