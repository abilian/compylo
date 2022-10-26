import ast
from scopedMap import *
from symbol import *

class TypeVisitor(ast.NodeVisitor):
    """
        Visitor that types the symbols within a map
    """

    def __init__(self, scopedMap):
        self._map: ScopedMap = scopedMap
        self._currentScope: str = 'global'

    def __safe_update(self, sym):
        if not self._map.update(sym): # if we just added a symbol
            self._map.remove(sym)
            raise Exception(f'Undefined symbol in scope {self._currentScope}: {sym}')

    def visit_Constant(self, node):
        return type(node.value).__name__

    def visit_Name(self, node):
        return self._map.find(node.id).type

    def visit_FunctionDef(self, node):
        save = self._currentScope
        self._map.old.append(self._currentScope)
        self._currentScope = node.name
        self._map.current = node.name

        self.visit(node.args)

        self._currentScope = save
        self._map.current = save
        self._map.old.pop()

    def visit_arguments(self, node):
        for a in node.args:
            self.visit(a)

    def visit_arg(self, node):
        sym = Symbol(node.arg, node.annotation.id)
        self.__safe_update(sym)


    def visit_Assign(self, node):
        typ = self.visit(node.value)
        sym = Symbol('', typ)
        for t in node.targets:
            sym.name = t.id
            self.__safe_update(sym)

    def visit_AnnAssign(self, node):
        sym = Symbol(node.target.id, node.annotation.id)
        self.__safe_update(sym)
