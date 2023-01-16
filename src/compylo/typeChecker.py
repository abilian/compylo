import ast

from .errors import IncompatibleTypeError
from .types import Int, String
from .visitor import NodeVisitor


class TypeChecker(NodeVisitor):
    """
    @brief Visitor that checks if the operations on types are logicals
    """

    def __checkType(self, t1, t2):
        if not t1.compatible_with(t1, t2):
            raise IncompatibleTypeError(t1, t2)

    def visit_Call(self, node: ast.Call):
        """
        @brief          Checks that the arguments with wich the function is
                        called are typed according to the arguments to function
                        was defined with
        @param  node    Call to be visited
        """
        expectedArgs = node.definition.args.args
        gottenArgs = node.args

        assert len(expectedArgs) == len(gottenArgs)

        # Check arguments
        for i in range(len(expectedArgs)):
            self.__checkType(expectedArgs[i].typ, gottenArgs[i].typ)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """
        @brief          Checks that the value type and target type are identical
        @param  node    AnnAssign to be visited
        """
        self.__checkType(node.target.typ, node.value.typ)

    def visit_BinOp(self, node: ast.BinOp):
        """
        @brief          Checks if the parts of the binop can be used with said
                        BinOp
        @param  node    BinOp to be visited
        """
        if isinstance(node.op, ast.Mult):
            if (node.left.typ, node.right.typ) == (String, Int) or (
                node.left.typ,
                node.right.typ,
            ) == (Int, String):
                return

        self.__checkType(node.left.typ, node.right.typ)
