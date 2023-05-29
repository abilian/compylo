import ast

from .errors import StatementOutOfLoopError, UnknownSymbolError
from .scopes import ScopedMap
from .symbol import Symbol
from .visitor import NodeVisitor


class Binder(NodeVisitor):
    """
    @brief First visitor to be ran. Adds an attribute `definition` to ast nodes
    """

    def __init__(self):
        self.map = ScopedMap()  # Scope
        self.loop = (
            None  # Loop we're curently in (needed for break and continue)
        )

    def __call__(self, node):
        self.visit(node)
        return self.map

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        @brief          Creates a symbol for the function and sets the node's
                        definition to itself
        @param  node    FunctionDef to be visited
        """

        sym = Symbol(node.name, definition=node)
        self.map.append(sym)
        node.definition = node

        self.map.push_scope(sym)
        self.visit(node.args)
        self.visit_list(node.body)

        self.map.pop_scope()

    def visit_arg(self, node: ast.arg):
        """
        @brief          Creates a new symbol for the argument, and sets the
                        node's definition to itself
        @param  node    arg to be visited
        """
        sym = Symbol(node.arg, definition=node)
        self.map.append(sym)
        node.definition = node

    def visit_Call(self, node: ast.Call):
        """
        @brief          Visits the Call node
        @param  node    Call to be visited
        """
        self.visit(node.func)
        self.visit_list(node.args)
        node.definition = node.func.definition

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """
        @brief          Visit the terms of the equality, but not the annotation.
                        will likely be removed at some point
        @param  node    AnnAssign to be visited
        """
        self.visit(node.target)
        self.visit(node.value)

    def visit_Name(self, node):
        """
        @brief          If the context is ast.Load, check for the symbol in the
                        symbol table, raise UnknownSymbolError if not found,
                        else sets the node's definition to the symbol's.
                        If the context is ast.Store, creates a new symbol and
                        sets the node's definition to itself.
        @param  node    Name to be visited
        """
        sym = self.map.find(node.id, False)
        if sym is not None:
            node.definition = sym.definition
            return

        match node.ctx:
            case ast.Load():
                raise UnknownSymbolError(node.id)
            case ast.Store():
                sym = Symbol(node.id, definition=node)
                self.map.append(sym)
                node.definition = node
            case _:
                raise NotImplementedError("del instruction not yet implemented")

    def visit_While(self, node: ast.While):
        """
        @brief          Sets self.loop properly
        @param  node    While to be visited
        """
        node.definition = node

        save = self.loop
        self.loop = node

        self.visit(node.test)
        self.visit_list(node.body)
        self.visit_list(node.orelse)

        self.loop = save

    def visit_Continue(self, node: ast.Continue):
        """
        @brief          Sets definition
        @param  node    ast.Continue to be played
        """
        if self.loop is None:
            raise StatementOutOfLoopError("while")

        node.definition = self.loop

    def visit_Break(self, node: ast.Break):
        """
        @brief          Sets definition
        @param  node    ast.Break to be played
        """
        if self.loop is None:
            raise StatementOutOfLoopError("break")

        node.definition = self.loop
