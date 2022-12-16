import ast
from .visitor import NodeTransformer


class DesugarVisitor(NodeTransformer):
    def __call__(self, node):
        self.visit(node)

    def visit_BinOp(self, node):
        pass

    def visit_Compare(self, node):
        pass

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
