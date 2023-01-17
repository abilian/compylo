import ast

from .binder import Binder
from .typeChecker import TypeChecker
from .typeInference import TypeInference
from .visitor import NodeTransformer
from .types import Int, String


class DesugarVisitor(NodeTransformer):
    def __call__(self, node):
        n = self.visit(node)
        Binder()(n)
        TypeInference()(n)
        TypeChecker()(n)
        return n

    def __desugar_IntString(self, right, left):
        st = right if right.typ == String else left
        num = right if right.typ == Int else left
        # FIXME: st/num can also be Subscript, Name, Function...
        if type(st) == ast.Constant and type(num) == ast.Constant:
            return ast.Constant(st.value * num.value)

        return None

    def visit_BinOp(self, node):
        if type(node.op) != ast.Mult:
            return node

        match (node.left.typ, node.right.typ):
            case (String, Int) | (Int, String):
                res = self.__desugar_IntString(node.right, node.left)
                return res if res is not None else node
            case _:
                return node

    def visit_Compare(self, node: ast.Compare):
        opsLen = len(node.ops)
        assert opsLen == len(node.comparators)
        if opsLen == 1:
            return node

        groups = []
        left = node.left
        for i in range(opsLen):
            right = node.comparators[i]
            compare = ast.Compare(left, [node.ops[i]], [right])
            groups.append(compare)
            left = right

        return ast.BoolOp(ast.And(), groups)

    def visit_AugAssign(self, node: ast.AugAssign):
        """
        @brief          Transforms `a += b` in `a = a + b`
        @param  node    AugAssign to be transformed
        """
        return ast.Assign([node.target], ast.BinOp(node.target, node.op,
                                                   node.value))

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
