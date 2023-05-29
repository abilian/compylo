import ast

from .binder import Binder
from .renamer import Renamer
from .type_checker import TypeChecker
from .type_inference import TypeInference
from .types import Int, String
from .visitor import NodeTransformer


class DesugarVisitor(NodeTransformer):
    def __call__(self, node):
        n = self.visit(node)
        Binder()(n)
        Renamer()(n)
        TypeInference()(n)
        TypeChecker()(n)
        return n

    def __desugar_IntString(self, right, left):
        st = right if right.typ == String else left
        num = right if right.typ == Int else left
        # FIXME: st/num can also be Subscript, Name, Function...
        match st, num:
            case ast.Constant, ast.Constant:
                return ast.Constant(st.value * num.value)
            case _:
                return None

    def visit_BinOp(self, node):
        """
        @brief          Desugaring common BinOp tricks, such as `a * "a"`
        @param  node    BinOp to be visited
        """
        if type(node.op) != ast.Mult:
            return node

        match (node.left.typ, node.right.typ):
            case (String, Int) | (Int, String):
                res = self.__desugar_IntString(node.right, node.left)
                return res if res is not None else node
            case _:
                return node

    def visit_Compare(self, node: ast.Compare):
        """
        @brief          Turns `a < b < c` into `a < b and b < c` (from Python doc)
        @param  node    Compare to be visited
        """
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

        return self.visit(
            ast.BoolOp(ast.And(), groups)
        )  # desugaring the And list as we go

    def visit_AugAssign(self, node: ast.AugAssign):
        """
        @brief          Transforms `a += b` in `a = a + b`
        @param  node    AugAssign to be visited
        """
        copy = node.target
        if isinstance(copy, ast.Name):
            copy.ctx = ast.Load()

        return ast.Assign([node.target], ast.BinOp(copy, node.op, node.value))

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

    def visit_BoolOp(self, node: ast.BoolOp):
        """
        @brief          Turns a BoolOp with more than 2 values into multiple
                        BoolOp within each other
        @param  node    BoolOp to be visited

        For some reason, BoolOp is not a binary operator.
        `1 and 2 and 3` is a single node in the ast, but this is a problem for
        later translation. So turning into a chain of binary nodes
        """
        assert len(node.values) > 1
        if len(node.values) == 2:
            return node  # the node is binary, stop there:

        left = node.values.pop(0)
        right = self.visit(node)

        return ast.BoolOp(node.op, [left, right])
