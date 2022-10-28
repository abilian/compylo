from errors import UnknownTypeError, IncompatibleTypeError
from visitor import NodeVisitor
import ast


class TypeVisitor(NodeVisitor):
    """
    Visitor that types the symbols within a map
    """

    def __init__(self):
        self.typeMap = {"int": None, "str": None, "float": None, "bool": None}

    def __call__(self, node):
        self.visit(node)

    def _are_compatible(self, typ1, typ2):
        return True

    def __exists(self, typ):
        """
        Checks if the type `typ` exists
        """
        return typ in self.typeMap.keys()

    def __update_Node(self, node, typ):
        if self.__exists(typ):
            node.typ = typ
        else:
            raise UnknownTypeError(typ)

    def visit_FunctionDef(self, node):
        """
        Adds the `typ` attribute to the node, using annotation
        """
        self.__update_Node(node, node.returns.id)

        self.visit(node.args)
        self.visit_list(node.body)

    def visit_arg(self, node):
        typ = node.annotation.id
        node.typ = typ

    def visit_Call(self, node):
        node.typ = node.definition.typ

    def visit_AnnAssign(self, node):
        self.visit(node.value)
        typ = node.annotation.id

        if not self._are_compatible(typ, node.value.typ):
            raise IncompatibleTypeError(typ, node.value.typ)

        node.target.typ = typ

    def visit_Assign(self, node):
        self.visit(node.value)
        typ = node.value.typ

        for t in node.targets:
            t.typ = typ

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            node.typ = node.definition.typ
        elif isinstance(node.ctx, ast.Store):
            pass
        else:
            raise NotImplementedError("del operator not yet implemented")

    def visit_Constant(self, node):
        node.typ = type(node.value).__name__

    def visit_BinOp(self, node):
        pass
