import ast

from llvmlite import ir

from .types import *
from .visitor import NodeVisitor


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
            Void: ir.VoidType(),
            String: ir.IntType(8).as_pointer(),
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
        self.visit_list(node.args.args)

        # visit the body
        self.visit_list(node.body)

        # FIXME: equivalent of llvmBuilder<>::restoreIP() in llvmlite

    def _createFunctionType(self, node):
        retType = self._typesMap[node.typ]
        argsType = [self._typesMap[a.typ] for a in node.args.args]

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
        @brief          Generates a load or an alloca depending on the context
        @param  node    Name to be visited
        """
        # create a store, load or smth instruction depending on node.ctx
        if isinstance(node.ctx, ast.Load):
            return self._builder.load(self._allocated[node.id])
        elif isinstance(node.ctx, ast.Store):
            return self._newAlloca(node, node.id)
        else:
            raise NotImplementedError("del operator not yet implemented")

    def visit_Assign(self, node: ast.Assign):
        """
        @brief          Creates the allocas and the store of the value for each
                        target
        @param  node    Assign to be visited
        """
        value = self.visit(node.value)
        self.visit_list(node.targets)  # creating the allocas

        stores = [
            self._builder.store(value, self._allocated[n.id])
            for n in node.targets
        ]

        return stores[-1]

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """
        @brief          Generates an alloca and a store for the variable
        @param  node    AnnAssign to be visited
        """
        value = self.visit(node.value)

        if not self._allocated[node.target.id]:
            self.visit(node.target)

        return self._builder.store(value, self._allocated[node.target.id])

    def visit_BinOp(self, node):
        """
        @brief          Creates the instruction corresponding to the binOp
        @param  node    BinOp to be visited
        """
        # typ is an instance of Singleton, so isinstance doesn't work
        assert node.left.typ == Int
        assert node.right.typ == Int

        funMap = {
            ast.Add: self._builder.add,
            ast.Sub: self._builder.sub,
            ast.Mult: self._builder.mul,
            ast.Div: self._builder.fdiv,
            ast.FloorDiv: self._builder.sdiv,
        }

        return funMap[type(node.op)](
            self.visit(node.left), self.visit(node.right)
        )

    def visit_If(self, node: ast.If):
        """
        @brief          Creates the basic blocks corresponding to an If
                        statement
        @param  node    If to be visited
        """
        pred = self.visit(node.test)
        if node.orelse != []:  # if there is an else statement
            with self._builder.if_else(pred) as (then, otherwise):
                with then:
                    self.visit_list(node.body)
                with otherwise:
                    self.visit_list(node.orelse)
        else:
            with self._builder.if_then(pred):
                self.visit_list(node.body)

    def visit_Compare(self, node: ast.Compare):
        """
        @brief          Creates the instruction for comparison
        @param  node    Compare to be visited
        """
        assert len(node.ops) == 1

        opMap = {
            ast.Eq: "==",
            ast.NotEq: "!=",
            ast.Gt: ">",
            ast.GtE: ">=",
            ast.Lt: "<",
            ast.LtE: "<=",
        }
        op = node.ops[0]

        return self._builder.icmp_signed(
            opMap[type(op)],
            self.visit(node.left),
            self.visit(node.comparators[0]),
        )
