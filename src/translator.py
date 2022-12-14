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
        self._functionMap = {}
        self._typesMap = {
            Int: ir.IntType(64),
            Float: ir.DoubleType(),
            Bool: ir.IntType(1),
            Void: ir.VoidType()
            # str: ir.ArrayType(X * i8) how ?
        }
        self._allocated = {}

    def __call__(self, node):
        self.visit(node)
        print(self.module)

    def _newAlloca(self, node, name):
        alloca = self._builder.alloca(self._typesMap[node.typ])
        self._allocated[name] = alloca
        return alloca

    def _visitFunctionBody(self, node):
        func = self._functionMap[node.name]
        # FIXME: equivalent of llvmBuilder<>::saveIP() in llvmlite

        entry = func.append_basic_block()  # function basic block
        self._builder.position_at_end(entry)  # start at end of basic block
        # TODO: - create alloca/store for each arg
        self.visit_list(node.args.args)

        # visit the body
        self.visit_list(node.body)

        # FIXME: equivalent of llvmBuilder<>::restoreIP() in llvmlite

    def _createFunctionType(self, node):
        retType = self._typesMap[node.typ]
        # argsType = [self._typesMap[a.annotation.id] for a in node.args.args]
        argsType = []
        for a in node.args.args:
            argsType.append(self._typesMap[a.typ])

        # FIXME: check for return type, might be void

        ftype = ir.FunctionType(retType, argsType)
        func = ir.Function(self.module, ftype, name=node.name)
        self._functionMap[node.name] = func

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        @brief          Creates the basic block corresponding to the function
        @param  node    FunctionDef to be visited
        """
        self._createFunctionType(node)
        self._visitFunctionBody(node)

    def visit_arg(self, node: ast.arg):
        """
        @brief          Creates the alloca for the argument
        @param  node    arg to be visited
        """
        return self._newAlloca(node, node.arg)

    def visit_Return(self, node: ast.Return):
        """
        @brief
        @param  node    Return to be visited
        """
        return self._builder.ret(self.visit(node.value))

    def visit_Call(self, node: ast.Call):
        """
        @brief          Creates a call instr
        @param  node    Call to be visited
        """
        return self._builder.call(
            self._functionMap[node.func.id], map(self.visit, node.args)
        )

    def visit_Constant(self, node):
        """
        @brief          Creates a constant using the node's typ and value.
        @param  node    Constant to be visited
        """
        # create a constant.
        return ir.Constant(self._typesMap[node.typ], node.value)

    def visit_Name(self, node):
        """
        @brief
        @param  node    Name to be visited
        """
        # create a store, load or smth instruction depending on node.ctx
        if isinstance(node.ctx, ast.Load):
            return self._builder.load(self._allocated[node.id])
        elif isinstance(node.ctx, ast.Store):
            return self._newAlloca(node, node.id)
        else:
            raise NotImplementedError("del operator not yet implemented")

    def visit_BinOp(self, node):
        """
        @brief          Creates the instruction corresponding to the binOp
        @param  node    BinOp to be visited
        """
        # typ is an instance of Singleton, so isinstance doesn't work
        assert node.left.typ == Int
        assert node.right.typ == Int

        match type(node.op):
            case ast.Add:
                return self._builder.add(
                    self.visit(node.left), self.visit(node.right)
                )
            case ast.Sub:
                return self._builder.sub(
                    self.visit(node.left), self.visit(node.right)
                )
            case ast.Mult:
                return self._builder.mul(
                    self.visit(node.left), self.visit(node.right)
                )
            case ast.Div:
                return self._builder.fdiv(
                    self.visit(node.left), self.visit(node.right)
                )
            case ast.FloorDiv:
                return self._builder.sdiv(
                    self.visit(node.left), self.visit(node.right)
                )
