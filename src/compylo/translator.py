import ast
from typing import Any

from llvmlite import ir

from .types import Bool, Float, Int, String, Void
from .visitor import NodeVisitor


class Translator(NodeVisitor):
    def __init__(self, triple=None):
        self._builder = ir.IRBuilder()
        self.module = ir.Module()
        self.module.triple = (
            triple if triple is not None else "x86_64-unknown-linux-gnu"
        )

        self._function_map = (
            {}
        )  # Maps the function name to the function block in LLVM
        self._loop_map = {}  # Maps each loop to the pair (testBB, endBB)
        self._types_map = {  # Maps the type from .types to LLVM Type
            Int: ir.IntType(64),
            Float: ir.DoubleType(),
            Bool: ir.IntType(1),
            Void: ir.VoidType(),
            String: ir.IntType(8).as_pointer(),
        }
        self._allocated = {}
        self._count = 0

    def __call__(self, node):
        self.visit(node)
        print(self.module)

    def _newAlloca(self, node, name):
        alloca = self._builder.alloca(self._types_map[node.typ])
        self._allocated[name] = alloca
        return alloca

    def _visitFunctionBody(self, node):
        func = self._function_map[node.name]
        # FIXME: equivalent of llvmBuilder<>::saveIP() in llvmlite

        entry = func.append_basic_block(
            f"{node.name}_entry"
        )  # function basic block
        self._builder.position_at_end(entry)  # start at end of basic block
        self.visit_list(node.args.args)

        # visit the body
        self.visit_list(node.body)

        # FIXME: equivalent of llvmBuilder<>::restoreIP() in llvmlite

    def _createFunctionType(self, node):
        retType = self._types_map[node.typ]
        args_type = [self._types_map[a.typ] for a in node.args.args]

        # FIXME: check for return type, might be void

        ftype = ir.FunctionType(retType, args_type)
        func = ir.Function(self.module, ftype, name=node.name)
        self._function_map[node.name] = func

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
            self._function_map[node.func.id], map(self.visit, node.args)
        )

    def visit_Constant(self, node):
        """
        @brief          Creates a constant using the node's typ and value.
        @param  node    Constant to be visited
        """
        # create a constant.
        if node.typ == Int or node.typ == Float:
            return ir.Constant(self._types_map[node.typ], node.value)

        if node.typ == Bool:
            return ir.Constant(self._types_map[node.typ], int(node.value))

        if node.typ == String:
            val = node.value + "\00"
            zero = ir.Constant(self._types_map[Int], 0)
            stringtype = ir.ArrayType(ir.IntType(8), len(val))
            var = ir.GlobalVariable(
                self.module, stringtype, "str.{self._count}"
            )
            var.initializer = ir.Constant(stringtype, bytearray(val, "ascii"))
            self._count += 1
            return var.gep((zero, zero))

        raise NotImplementedError(f"Type {node.typ} is not yet implemented")

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

        # stores = []
        # for n in node.targets:
        #    val = self._builder.store(value, self._allocated[n.id])
        #    stores.append(val)

        return stores[-1]

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """
        @brief          Generates an alloca and a store for the variable
        @param  node    AnnAssign to be visited
        """
        value = self.visit(node.value)
        self.visit(node.target)

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

        fun_map: dict[type(ast.AST), Any] = {
            ast.Add: self._builder.add,
            ast.Sub: self._builder.sub,
            ast.Mult: self._builder.mul,
            ast.Div: self._builder.fdiv,
            ast.FloorDiv: self._builder.sdiv,
        }

        return fun_map[type(node.op)](
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

    def visit_BoolOp(self, node: ast.BoolOp):
        """
        @brief          Creates the instruction
        @param  node    BoolOp to be visited
        """
        assert len(node.values) == 2

        left = self.visit(node.values[0])
        right = self.visit(node.values[1])

        # FIXME: "aa" and "bb breaks this"
        assert isinstance(left.type, ir.IntType) and isinstance(
            right.type, ir.IntType
        )
        maxType = max(
            ((x.width, x) for x in [left.type, right.type]),
            key=lambda t: t[0],
        )[1]

        if left.type != maxType:
            left = self._builder.sext(left, maxType)
        elif right.type != maxType:
            right = self._builder.sext(right, maxType)

        if type(node.op) == ast.And:
            instr = self._builder.and_(left, right)
        else:
            instr = self._builder.or_(left, right)

        return self._builder.trunc(instr, self._types_map[Bool])

    def visit_While(self, node: ast.While):
        """
        @brief          Translates the loop by creating 3 BB:
                        - 1 for the condition,
                        - 1 for the body,
                        - 1 for the loop exit.
        @param  node    While to be visited
        """
        testBlock = self._builder.append_basic_block(
            f"while{self._count}_test"
        )
        bodyBlock = self._builder.append_basic_block(
            f"while{self._count}_body"
        )
        endBlock = self._builder.append_basic_block(f"while{self._count}_end")
        self._loop_map[node] = (testBlock, endBlock)
        self._builder.branch(testBlock)

        self._builder.position_at_end(testBlock)
        testRes = self.visit(node.test)
        self._builder.cbranch(testRes, bodyBlock, endBlock)

        self._builder.position_at_end(bodyBlock)
        self.visit_list(node.body)
        self._builder.branch(testBlock)

        self._builder.position_at_end(endBlock)
        self.visit_list(node.orelse)

    def visit_Break(self, node: ast.Break):
        return self._builder.branch(self._loop_map[node.definition][1])

    def visit_Continue(self, node: ast.Continue):
        return self._builder.branch(self._loop_map[node.definition][0])
