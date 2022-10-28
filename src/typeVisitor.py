import ast
from scopedMap import *
from symbol import *


class TypeVisitor(ast.NodeVisitor):
    """
    Visitor that types the symbols within a map
    """

    def __init__(self, scopedMap):
        self._map: ScopedMap = scopedMap

    def visit_Constant(self, node):
        return type(node.value).__name__

    def visit_Name(self, node):
        pass

    def visit_FunctionDef(self, node):
        pass

    def visit_arguments(self, node):
        for a in node.args:
            self.visit(a)

    def visit_arg(self, node):
        pass

    def visit_Assign(self, node):
        pass

    def visit_AnnAssign(self, node):
        pass
