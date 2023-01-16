import ast

from .binder import Binder
from .typeChecker import TypeChecker
from .typeInference import TypeInference
from .visitor import NodeTransformer


class DesugarVisitor(NodeTransformer):
    def __call__(self, node):
        n = self.visit(node)
        Binder()(n)
        TypeInference()(n)
        TypeChecker()(n)
        return n

    def visit_BinOp(self, node):
        if type(node.op) != ast.Mult:
            return node

        match (node.left.typ, node.right.typ):
            case (String, Int) | (Int, String):
                st = node.right if node.right.typ == String else node.left
                num = node.right if node.right.typ == Int else node.left
                # FIXME: st/num can also be Subscript, Name, Function...
                if type(st) == ast.Constant and type(num) == ast.Constant:
                    return ast.Constant(st.value * num.value)
                else:
                    return node
            case _:
                return node

    def visit_Compare(self, node):
        return node

    def visit_UnaryOp(self, node):
        """
        @brief          Transforms -X in (0 - X)
        @param  node    UnaryOp to be visited
        """
        match type(node.op):
            case ast.UAdd:
                return node.operand
            case ast.USub:
                return ast.BinOp(ast.Constant(0), ast.Sub(), node.operand)
