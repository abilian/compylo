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

    def __printIndent(self, s=""):
        self.__print(Printer.Indent * " " + s)

    def __printWithDef(self, toPrint: str, node: ast.AST):
        self.__print(toPrint)
        if hasattr(node, "definition"):
            self.__print(f"__{self.__extract_address(node.definition)}")

    def __print(self, s: str):
        print(s, end="")

    def visit_list(self, l):
        for instr in l:
            self.__printIndent()
            self.visit(instr)
            print()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.__printIndent(f"def {node.name}")
        self.__printWithDef("", node)
        self.__print("(")

        self.visit(node.args)
        self.__print("):")

        self.__incrIndent()
        print()
        self.visit_list(node.body)
        self.__decrIndent()

    def visit_arg(self, node: ast.arg):
        self.__printWithDef(node.arg, node)
        if hasattr(node, "annotation"):
            self.__print(f" : {node.annotation.id}")
        self.__print(" ")

    def visit_Return(self, node: ast.Return):
        self.__print("return ")
        self.visit(node.value)
        print()

    def visit_Call(self, node: ast.Call):
        self.visit(node.func)
        print("(", end="")
        if node.args:
            l = len(node.args)
            self.visit(node.args[0])
            for i in range(1, l):
                print(", ", end="")
                self.visit(node.args[i])

        print(")", end="")

    def visit_AnnAssign(self, node: ast.AnnAssign):
        self.visit(node.target)
        self.__print(": ")
        self.visit(node.annotation)
        self.__print(" = ")
        self.visit(node.value)
        print()

    def visit_Assign(self, node: ast.Assign):
        for t in node.targets:
            self.visit(t)
            self.__print(" = ")

        self.visit(node.value)

    def visit_AugAssign(self, node: ast.AugAssign):
        opMap = {
            ast.Add: " += ",
            ast.Sub: " -= ",
            ast.Mult: " *= ",
            ast.Div: " /= ",
            ast.FloorDiv: " //= ",
        }
        self.visit(node.target)
        self.__print(opMap[type(node.op)])
        self.visit(node.value)

    def visit_Constant(self, node: ast.Constant):
        self.__print(node.value)

    def visit_Name(self, node: ast.Name):
        self.__printWithDef(node.id, node)

    def visit_If(self, node: ast.If):
        self.__print("if ")
        self.visit(node.test)
        self.__print(":")
        self.__incrIndent()
        self.visit_list(node.body)
        self.__decrIndent()

    def visit_Compare(self, node: ast.Compare):
        opMap = {
            ast.Eq: " == ",
            ast.NotEq: " != ",
            ast.Gt: " > ",
            ast.GtE: " >= ",
            ast.Lt: " < ",
            ast.LtE: " >= ",
        }

        self.visit(node.left)
        for i in range(len(node.comparators)):
            instr = node.comparators[i]
            op = node.ops[i]
            self.__print(opMap[type(op)])
            self.visit(instr)

    def visit_BinOp(self, node: ast.BinOp):
        self.visit(node.left)
        match type(node.op):
            case ast.Add:
                self.__print(" + ")
            case ast.Sub:
                self.__print(" - ")
            case ast.Mult:
                self.__print(" * ")
            case ast.Div:
                self.__print(" / ")
            case ast.FloorDiv:
                self.__print(" // ")
        self.visit(node.right)

    def visit_UnaryOp(self, node: ast.UnaryOp):
        match type(node.op):
            case ast.USub:
                self.__print("-")
            case ast.UAdd:
                self.__print("+")
        self.visit(node.operand)

    def visit_While(self, node: ast.While):
        self.__print("while ")
        self.visit(node.test)
        self.__printWithDef(": #", node)
        self.__print("\n")
        self.__incrIndent()
        self.visit_list(node.body)
        self.__decrIndent()
        if node.orelse != []:
            self.__print("else:")
            self.__incrIndent()
            self.visit_list(node.orelse)
            self.__decrIndent()

    def visit_Continue(self, node: ast.Continue):
        self.__printWithDef("continue # ", node)

    def visit_Break(self, node: ast.Break):
        self.__printWithDef("break #", node)
