from __future__ import annotations

import ast

import pytest

from compylo.binder import Binder
from compylo.desugar import DesugarVisitor
from compylo.errors import TypeCheckError, UnknownSymbolError
from compylo.renamer import Renamer
from compylo.type_checker import TypeChecker
from compylo.type_inference import TypeInference

simple_expressions = [
    # Literals
    "1",
    "1.0",
    "1e3",
    "1e-3",
    "True",
    "False",
    "'a'",
    '"a"',
    "f'a'",
    # Arithmetic
    "1+1",
    "2 * 3 + 5 * 6",
    "'a' + 'b'",
    "3 * 'a'",
    '"a" + "b"',
    "1 // 2",
    "1 % 2",
    # Constructors
    # "str(1)",
    # "int('1')",
    # "float('1.0')",
    # "bool(1)",
    # "bool(0)",
    # "bool(1.0)",
    # "bool(0.0)",
    # "bool('a')",
    # "bool('')",
    # "bool([1])",
    # "bool([])",
    # Lambda
    # "(lambda x: x)(3)",
    # Boolean expressions
    "True or False",
    "True and False",
    # Bitwise expressions
    "1 | 2",
    "1 & 2",
    "1 ^ 2",
    "1 << 2",
    "1 >> 2",
    # Comparison expressions
    "1 == 2",
    "1 != 2",
    "1 < 2",
    "1 <= 2",
    "1 > 2",
    "1 >= 2",
    # In expressions
    "1 in [1, 2]",
    "1 not in [1, 2]",
    "1 in (1, 2)",
    "1 not in (1, 2)",
    "1 in {1: 1}",
    "1 not in {1: 1}",
    "'a' in 'abc'",
    "'a' not in 'abc'",
    "'a' in ['a', 'b']",
    "'a' not in ['a', 'b']",
    "'a' in ('a', 'b')",
    "'a' not in ('a', 'b')",
    # If expressions
    "1 if True else 2",
    "1 if False else 2",
    # List and tuples expressions
    # "[1, 2] == [2, 1]",
    # "[1, 2] == list([1, 2])",
    # "[1, 2] == [x for x in [1, 2]]",
    # "[1, 2] == [x for x in (1, 2)]",
    # "[1, 2] == sorted([2, 1])",
    # "{k: k for k in 'abc'}",
    # Str
    # "str(1.0) == '1.'",
    # "str(1e3) == '1000.'",
    # Lists
    "[]",
    "[1]",
    "[1, 2]",
    "{'a': 1}",
    # Str (nope)
    # "str(True)",
    # "str(False)",
    # "str(True) == 'True'",
    # "str(False) == 'False'",
    # Tupes (nope)
    # "(1, 2)",
    # Set expressions (nope)
    # "1 in {1}",
    # "1 not in {1}",
    # "{1, 2} == {2, 1}",
    # Dict
    "{}",
    "{'a': 1}",
    # "list({'a': 1})",
    # "list({'a': 1}.keys())",
    # "list({'a': 1}.values())",
    # "{'a': 1} == {'a': 1}",
    # "dict(a=1) == {'a': 1}",
    # "dict([('a', 1)]) == {'a': 1}",
    # Fail
    # "{1: 1}",
    # "list({'a': 1}.items())",
]


@pytest.mark.parametrize("expression", simple_expressions)
def test_compile(expression: str):
    compile(expression)


def compile(source):
    ast_root = ast.parse(source)
    Binder()(ast_root)
    Renamer()(ast_root)
    TypeInference()(ast_root)
    TypeChecker()(ast_root)
    DesugarVisitor()(ast_root)
