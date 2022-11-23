import ast
from .visitor import NodeVisitor
from .errors import IncompatibleTypeError


class TypeChecker(NodeVisitor):
    """
    @brief Visitor that checks if the operations on types are logicals
    """

    def __call__(self, node):
        self.visit(node)

    def __checkType(self, t1, t2):
        if t1 != t2:
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

        l = len(expectedArgs)
        assert l == len(gottenArgs)

        # Check arguments
        for i in range(l):
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

        self.__checkType(node.left.typ, node.right.typ)
