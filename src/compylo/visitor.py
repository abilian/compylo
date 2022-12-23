from ast import NodeVisitor as Visitor, NodeTransformer as Transformer


class NodeVisitor(Visitor):
    def visit_list(self, l):
        for instr in l:
            self.visit(instr)


class NodeTransformer(Transformer):
    def visit_list(self, l):
        for instr in l:
            self.visit(instr)
