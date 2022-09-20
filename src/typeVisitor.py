from scopedMap import *
from symbol import *
import ast

class TypeVisitor():
    def __init__(self, scopedMap):
        self.scopedMap = scopedMap

        self.typeDict = {
            'int': int,
            'str': str,
            'float': float,
            'bool': bool
        }

    def visit(self, node):
        name = 'visit' + type(node).__name__
        fct = getattr(self, name)

        return fct(node)

    def visitModule(self, node):
        print("visiting Module")
        for t in node.body:
            self.visit(t)


    def visitExpr(self, node):
        print("visiting Expr")
        self.visit(node.value)


    def visitBinOp(self, node):
        print("visiting BinOp")
        typeLeft = self.visit(node.left)
        typeRight = self.visit(node.right)

        if typeLeft != typeRight:
            raise TypeError(f'Cannot use operator {node.op} with terms of\
                            different types') # FIXME: need a way to say where we are in the program

        return typeRight


    def visitConstant(self, node):
        print("visiting Constant")
        return type(node.value)


    def visitAssign(self, node):
        """
            For now, assuming we're just doing assignments like `x = 1`
        """
        print("visiting Assign")
        for t in node.targets:
            s = Symbol(t.id)
            s.type = self.visit(node.value)

        pass


    def visitEq(self, node):
        print("visiting Eq")
        pass


    def visitCall(self, node):
        print("visiting Call")
        pass


    def visitFunctionDef(self, node):
        """
            - Create a new symbol for the function
            - Check the body for a Return node
                If so, s.type = return.type
                Else s.type = Void
            visit the body
        """
        print("visiting FunctionDef")
        pass


    def visitArguments(self, node):
        print("visiting Arguments")
        pass


    def visitArg(self, node):
        print("visiting Arg")
        pass


    def visitReturn(self, node):
        print("visiting Return")
        pass


    def visitName(self, node):
        print("visiting Name")
        pass


    def visitLoad(self, node):
        print("visiting Load")
        pass


    def visitIf(self, node):
        print("visiting If")
        pass


    def visitStore(self, node):
        pass


if __name__ == '__main__':
    with open('./toto.py') as f:
        content = f.read()

    root = ast.parse(content)
    TypeVisitor(None).visitModule(root)
