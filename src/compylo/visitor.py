from ast import NodeTransformer as Transformer
from ast import NodeVisitor as Visitor


class NodeVisitor(Visitor):
    def __call__(self, node):
        self.visit(node)

    def visit_list(self, li):
        for instr in li:
            self.visit(instr)


class NodeTransformer(Transformer):
    def visit_list(self, li):
        for instr in li:
            self.visit(instr)
