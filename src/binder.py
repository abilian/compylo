from scopedMap import ScopedMap
from symbol import Symbol
import ast

class Binder(ast.NodeVisitor):
    """
    First visitor to be ran, can most likely be refactor-ed within the other
    visitors. It just fills the a scopedMap with symbols.
    """

    def __init__(self):
        self.map = ScopedMap()

    def visit_FunctionDef(self, node):
        # First, add the function symbol
        sym = Symbol(node.name, definition=node)
        self.map.append(sym)

        # Then, add a scope corresponding to the function
        self.map.push_scope(sym)
        self.visit(node.args)
        for instr in node.body:
            self.visit(instr)

        self.map.pop_scope()

    def visit_arguments(self, node):
        for a in node.args:
            self.visit(a)

    def visit_arg(self, node):
        sym = Symbol(node.arg, definition=node)
        self.map.append(sym)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        self.visit(node.target)
        self.visit(node.value)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            sym = self.map.find(node.id)
            if sym is None:
                raise Exception(f'Undefined symbol: {node.id}')
            node.definition = sym.definition
        elif isinstance(node.ctx, ast.Store):
            sym = Symbol(node.id, definition=node)
            self.map.append(sym)
        else:
            raise NotImplementedError('del instruction not yet implemented')
