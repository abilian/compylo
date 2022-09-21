from scopedMap import *
from symbol import *
import ast

class TypeVisitor():
    ifCounter = 0

    def __init__(self, scopedMap):
        self.scopedMap = scopedMap

        self.typeDict = {
            'int': int,
            'str': str,
            'float': float,
            'bool': bool
        }

    def _visitWithPredicate(self, node, predicate):
        # TODO: Useful, can be used to find a return statement embedded
        # somewhere in a function, or smth like that
        pass

    def visit(self, node):
        t = type(node).__name__
        if (t[0].islower()): # prettier code
            t = t[0].upper() + t[1:]

        name = 'visit' + t
        fct = getattr(self, name)

        return fct(node)

    def visitModule(self, node):
        print('visiting Module')
        for t in node.body:
            self.visit(t)


    def visitExpr(self, node):
        print('visiting Expr')
        return self.visit(node.value)


    def visitBinOp(self, node):
        '''
            FIXME: Pb: In Python, we can multiply string or float by int... How to
            check for that ? In general, how to check for overloaded binary
            operators ?
        '''
        print('visiting BinOp')
        typeLeft = self.visit(node.left)
        typeRight = self.visit(node.right)

        if typeLeft != typeRight:
            raise TypeError(f'Cannot use operator {node.op} with terms {typeLeft.__name__} and {typeRight.__name__}')
        # FIXME: need a way to say where we are in the program

        return typeRight


    def visitConstant(self, node):
        print('visiting Constant')
        return type(node.value).__name__


    def visitAssign(self, node):
        '''
            For now, assuming we're just doing assignments like `x = 1`
        '''
        print('visiting Assign')
        for t in node.targets:
            s = Symbol(t.id)
            self.scopedMap.append(s) # Should it be append or update ?
            s.type = self.visit(node.value)


    def visitCall(self, node):
        print('visiting Call')
        self.visit(node.func)
        for a in node.args:
            self.visit(a)

        sym = self.scopedMap.find(node.func.id) # FIXME: what is node.func is
                                                # not an ast.Name ? Can it ?
        if sym is None:
            raise NotImplementedError(f'No symbol to call for {node.func.id}')

        return sym.type


    def visitFunctionDef(self, node):
        '''
            - Create a new symbol for the function
            - Check the body for a Return node
                If so, s.type = return.type
                Else s.type = Void
            visit the body
        '''
        # FIXME: For now, only handling functions with annotations
        print('visiting FunctionDef')
        s = Symbol(node.name)
        s.type = node.returns.id
        self.scopedMap.update(s)
        self.scopedMap.push_scope(node.name)

        self.visit(node.args)

        for e in node.body:
            self.visit(e)

        self.scopedMap.pop_scope()

    def visitArguments(self, node):
        print('visiting Arguments')
        # FIXME: incomplete
        for a in node.args:
            self.visit(a)


    def visitArg(self, node):
        print('visiting Arg')
        s = Symbol(node.arg)
        if node.annotation:
            s.type = node.annotation.id


    def visitReturn(self, node):
        print('visiting Return')
        return self.visit(node.value)


    def visitIf(self, node):
        print('visiting If')
        self.visit(node.test)

        self.scopedMap.push_scope(f'if__{TypeVisitor.ifCounter}')
        TypeVisitor.ifCounter += 1

        for e in node.body:
            self.visit(e)

        print(self.scopedMap)

        self.scopedMap.pop_scope()

    def visitName(self, node):
        print("visiting Name")
        pass


    def visitCompare(self, node):
        print('visiting Compare')
        self.visit(node.left)
        for c in node.comparators:
            self.visit(c)


if __name__ == '__main__':
    with open('./toto.py') as f:
        content = f.read()

    root = ast.parse(content)
    scopedMap = ScopedMap()
    t = TypeVisitor(scopedMap)
    t.visitModule(root)
