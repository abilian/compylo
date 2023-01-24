import ast

from .visitor import NodeVisitor


class Renamer(NodeVisitor):
    """
    @brief  Renamer class, changes information about the nodes in place. Chosen
            format is `nodeName__X` where X is a static counter incremented at
            each renaming
    """

    def __init__(self):
        self._counter = 0
        self._defMap = {} # mapping of definition with their names

    def __gen_Name(self, name: str):
        res = f"{name}__{self._counter}"
        self._counter += 1
        return res

    def __change_Name_id(self, node: ast.Name, definition):
        match type(definition):
            case ast.Name:  # classic variable
                node.id = definition.id
            case ast.arg:  # function argument
                node.id = definition.arg
            case ast.FunctionDef:  # function call
                node.id = definition.name
            case _:
                raise NotImplementedError("This is weird")

    def visit_FunctionDef(self, node):
        newName = self.__gen_Name(node.name)
        node.name = newName
        self._defMap[node.definition] = newName

        self.visit(node.args)
        self.visit_list(node.body)

    def visit_arg(self, node):
        node.arg = self.__gen_Name(node.arg)
        self._defMap[node.definition] = node.arg

    def visit_AnnAssign(self, node):
        self.visit(node.target)
        self.visit(node.value)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            if node.definition in self._defMap:
                node.id = self.__gen_Name(node.id)
                self._defMap[node.definition] = node.id
            else:
                self.__change_Name_id(node, node.definition)
        elif isinstance(node.ctx, ast.Load):
            self.__change_Name_id(node, node.definition)
        else:
            raise NotImplementedError("del instruction not implemented yet")
