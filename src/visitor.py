import ast


class NodeVisitor(ast.NodeVisitor):
    def visit_list(self, l):
        for instr in l:
            self.visit(instr)
