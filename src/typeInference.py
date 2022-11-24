from .errors import UnknownTypeError
from .visitor import NodeVisitor
from .types import Int, Float, Bool, String
import ast


class TypeInference(NodeVisitor):
    """
    @brief Visitor that adds a `typ` attribute into nodes, holding the type
    """

    def __init__(self):
        self.typeMap = {
            "int": Int,
            "str": String,
            "float": Float,
            "bool": Bool,
        }

    def __call__(self, node):
        self.visit(node)

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

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        @brief              Adds the `typ` attribute to the node, using annotation
        @param      node    FunctionDef to be visited
        """
        self.__update_Node(node, node.returns.id)

        self.visit(node.args)
        self.visit_list(node.body)

    def visit_arg(self, node: ast.arg):
        """
        @brief          Sets the node's typ to its annotation.
        @param  node    arg to be visited
        """
        typ = node.annotation.id
        node.typ = self.typeMap[typ]

    def visit_Call(self, node: ast.Call):
        """
        @brief          Sets the node's type to its definition's
        @param  node    Call to be visited
        """
        node.typ = node.definition.typ
        self.visit_list(node.args)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """
        @brief          Sets the node's type to its annotation
        @param  node    AnnAssign to be visited
        """
        self.visit(node.value)
        typ = node.annotation.id

        if not self.__exists(typ):
            raise UnknownTypeError(typ)

        node.target.typ = self.typeMap[typ]

    def visit_Assign(self, node: ast.Assign):
        """
        @brief          Sets the targets's `typ` to the value's
        @param  node    Assign to be visited
        """
        self.visit(node.value)
        typ = node.value.typ

        for t in node.targets:
            t.typ = typ

    def visit_Name(self, node: ast.Name):
        """
        @brief          If the context is ast.Load, sets the node's typ to its
                        definition's.
                        If the context is an ast.Store, pass, as the type will
                        be set somewhere else
        @param  node    Name to be visited
        """
        if isinstance(node.ctx, ast.Load):
            node.typ = node.definition.typ
        elif isinstance(node.ctx, ast.Store):
            pass
        else:
            raise NotImplementedError("del operator not yet implemented")

    def visit_Constant(self, node):
        """
        @brief          Sets the constant's type to the type of its value
        @param  node    Constant to be visited
        """
        node.typ = self.typeMap[type(node.value).__name__]
