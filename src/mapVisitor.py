from scopedMap import ScopedMap
from symbol import Symbol
import ast

class MapVisitor(ast.NodeVisitor):
    """
        First visitor to be ran, can most likely be refactor-ed within the other
        visitors. It just fills the a scopedMap with symbols.
    """
    def __init__(self):
        self.map = ScopedMap()

    def visit_FunctionDef(self, node):
        self.map.push_scope(node.name)
        self.visit(node.args)
        self.map.pop_scope()

    def visit_arguments(self, node):
        for a in node.args:
            self.visit(a)

    def visit_arg(self, node):
        sym = Symbol(node.arg)
        self.map.update(sym)

    def visit_Assign(self, node):
        for t in node.targets:
            sym = Symbol(t.id)
            self.map.update(sym)

    def visit_AnnAssign(self, node):
        sym = Symbol(node.target.id)
        self.map.update(sym)


if __name__ == '__main__':
    with open('./toto.py') as f:
        content = f.read()

    root = ast.parse(content)
    scopedMap = ScopedMap()
    t = MapVisitor()
    t.visit(root)
    print(t.map)
