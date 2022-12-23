from ast import NodeTransformer as Transformer
from ast import NodeVisitor as Visitor


class NodeVisitor(Visitor):
    def visit_list(self, l):
        for instr in l:
            self.visit(instr)


class NodeTransformer(Transformer):
    def visit_list(self, l):
        for instr in l:
            self.visit(instr)
