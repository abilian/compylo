import ast


class Renamer(ast.NodeVisitor):
    counter = 0

    def __call__(self, ast):
        self.visit(ast)

    def __gen_Name(self, name: str):
        res = f"{name}__{Renamer.counter}"
        Renamer.counter += 1
        return res

    def visit_FunctionDef(self, node):
        newName = self.__gen_Name(node.name)
        node.name = newName

        self.visit(node.args)
        for instr in node.body:
            self.visit(instr)

    def visit_arg(self, node):
        node.arg = self.__gen_Name(node.arg)

    def visit_AnnAssign(self, node):
        self.visit(node.target)
        self.visit(node.value)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            node.id = self.__gen_Name(node.id)
        elif isinstance(node.ctx, ast.Load):
            match type(node.definition):
                case ast.Name:  # classic variable
                    node.id = node.definition.id
                case ast.arg:  # function argument
                    node.id = node.definition.arg
                case ast.FunctionDef:  # function call
                    node.id = node.definition.name
                case _:
                    raise NotImplementedError("This is weird")
        else:
            raise NotImplementedError("del instruction not implemented yet")
