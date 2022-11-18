from ast import NodeVisitor as Visitor


class NodeVisitor(Visitor):
    def visit_list(self, l):
        for instr in l:
            self.visit(instr)
