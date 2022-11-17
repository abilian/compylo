from .scopedMap import ScopedMap
from .symbol import Symbol
from .visitor import NodeVisitor
from .errors import UnknownSymbolError
import ast


class Binder(NodeVisitor):
    """
    First visitor to be ran, can most likely be refactor-ed within the other
    visitors. It just fills the a scopedMap with symbols.
    """

    def __init__(self):
        self.map = ScopedMap()

    def __call__(self, node):
        self.visit(node)
        return self.map

    def visit_FunctionDef(self, node):
        """
        Create a symbol for the function, adds it to the scoped map.
        Pushes a new scope and visits the function within this new scope
        """

        sym = Symbol(node.name, definition=node)
        self.map.append(sym)
        node.definition = node

        self.map.push_scope(sym)
        self.visit(node.args)
        self.visit_list(node.body)

        self.map.pop_scope()

    def visit_arg(self, node):
        """
        Creates a symbol for the arg, adds it to the map and sets the definition
        of the node to itself
        """
        sym = Symbol(node.arg, definition=node)
        self.map.append(sym)
        node.definition = node

    def visit_Call(self, node):
        self.visit(node.func)
        self.visit_list(node.args)

    def visit_AnnAssign(self, node):
        """
        Do not visit the annotation (temporary)
        """
        self.visit(node.target)
        self.visit(node.value)

    def visit_Name(self, node):
        """
        Visits a name.
        If context is `ast.Load`, variable is used as rValue
            -> look it up in the table and throw error if undefined
        Else if context is `ast.Store`, variable is used a lValue
            -> create a new symbol and sets the definition of the node.
            FIXME: for AugAssign, this doesn't work
        Else (context is `ast.Del`)
           -> remove the symbol ? FIXME: Not Implemented
        """
        if isinstance(node.ctx, ast.Load):
            sym = self.map.find(node.id, False)
            if sym is None:
                raise UnknownSymbolError(node.id)
            node.definition = sym.definition
        elif isinstance(node.ctx, ast.Store):
            sym = Symbol(node.id, definition=node)
            self.map.append(sym)
            node.definition = node
        else:
            raise NotImplementedError("del instruction not yet implemented")
