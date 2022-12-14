from llvmlite import ir
from .types import *
from .visitor import NodeVisitor
import ast


class Translator(NodeVisitor):
    def __init__(self, triple=None):
        self._builder = ir.IRBuilder()
        self.module = ir.Module()
        self.module.triple = (
            triple if triple is not None else "x86_64-unknown-linux-gnu"
        )
        self._functionMap = {}  # FIXME: still useful ?
        self._currentFunction = None
        self._typesMap = {
            Int: ir.IntType(64),
            Float: ir.DoubleType(),
            Bool: ir.IntType(1),
            Void: ir.VoidType()
            # str: ir.ArrayType(X * i8) how ?
        }

    def __call__(self, node):
        self.visit(node)
        print(self.module)

    def _visitFunctionBody(self, node):
        func = self._functionMap[node.name]
        old_func = self._currentFunction  # save in case of nested functions
        self._currentFunction = func
        # FIXME: equivalent of llvmBuilder<>::saveIP() in llvmlite

        entry = func.append_basic_block()  # function basic block
        self._builder.position_at_end(entry)  # start at end of basic block
        # TODO: - create alloca/store for each arg

        # visit the body
        for e in node.body:
            self.visit(e)

        # TODO: no return -> create void
        #       return -> else create ret

        # restore context of previous function
        self._currentFunction = old_func
        # FIXME: equivalent of llvmBuilder<>::restoreIP() in llvmlite

    def _createFunctionType(self, node):
        # FIXME: bancal ?
        retType = self._typesMap[node.typ]
        argsType = []

        for a in node.args.args:
            argsType.append(self._typesMap[a.annotation.id])

        ftype = ir.FunctionType(retType, argsType)
        func = ir.Function(self.module, ftype, name=node.name)
        self._functionMap[node.name] = func

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        @brief
        @param  node    FunctionDef to be visited
        """
        self._createFunctionType(node)
        self._visitFunctionBody(node)

    def visit_Return(self, node: ast.Return):
        """
        @brief
        @param  node    Return to be visited
        """
        self._builder.ret(self.visit(node.value))

    def visit_Constant(self, node):
        """
        @brief          Creates a constant using the node's typ and value.
        @param  node    Constant to be visited
        """
        # create a constant.
        return ir.Constant(self._typesMap[node.typ], node.value)

    def visitName(self, node):
        """
        @brief
        @param  node    Name to be visited
        """
        # create a store, load or smth instruction depending on node.ctx
        pass

    def visitBinOp(self, node):
        """
        node.op:
            Add()       -> _builder.add
            Sub()       -> _builder.sub
            Mult()      -> _builder.mul
            Div()       -> _builder.fdiv
            FloorDiv()  -> _builder.sdiv
        @brief
        @param  node    BinOp to be visited
        """
        pass
