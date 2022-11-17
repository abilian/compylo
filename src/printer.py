import ast
from .visitor import NodeVisitor


class Printer(NodeVisitor):
    Indent: int = 0

    def __extract_address(self, node: ast.AST):
        return str(node).split("at")[1][1:-1]

    def __incrIndent(self):
        Printer.Indent += 4

    def __decrIndent(self):
        Printer.Indent -= 4

    def __printWithDef(self, toPrint: str, node: ast.AST):
        self.__print(toPrint)
        if hasattr(node, "definition"):
            self.__print(f"__{self.__extract_address(node.definition)}")

    def __print(self, s: str):
        print(s, end="")

    def __call__(self, node: ast.AST) -> None:
        self.visit(node)

    def visit_FunctionDef(self, node):
        s: str = (Printer.Indent * " ") + f"def {node.name}"
        self.__printWithDef(s, node)
        self.__print("(")

        self.visit(node.args)
        self.__print("):")

        self.__incrIndent()
        print()
        self.visit_list(node.body)
        self.__decrIndent()

    def visit_Return(self, node):
        s: str = Printer.Indent * " "
        self.__print(s + "return ")
        self.visit(node.value)
        print()

    def visit_arg(self, node: ast.arg):
        self.__printWithDef(node.arg, node)
        if hasattr(node, "annotation"):
            self.__print(f" : {node.annotation.id}")
        self.__print(" ")

    def visit_AnnAssign(self, node: ast.AnnAssign):
        self.visit(node.target)
        self.__print(": ")
        self.visit(node.annotation)
        self.__print(" = ")
        self.visit(node.value)
        print()

    def visit_Constant(self, node: ast.Constant):
        self.__print(node.value)

    def visit_Name(self, node: ast.Name):
        self.__printWithDef(node.id, node)
