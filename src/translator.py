from llvmlite import ir
import ast


class Translator:
    def __init__(self, triple=None, trace=False):
        self._trace = trace
        self._builder = ir.IRBuilder()
        self._module = ir.Module()
        self._module.triple = (
            triple if triple is not None else "x86_64-unknown-linux-gnu"
        )
        self._functionMap = {}
        self._currentFunction = None
        self._typesMap = {
            "int": ir.IntType(64),
            "float": ir.DoubleType(),
            "None": ir.VoidType()
            # str: ir.ArrayType(X * i8) how ?
        }

    def visit(self, node):
        t = type(node).__name__
        if t[0].islower():
            t = t[0].upper() + t[1:]

        name = "visit" + t
        fct = getattr(self, name)

        if self._trace:
            print(f"Visiting {t}")

        return fct(node)

    def visitModule(self, node):
        for n in node.body:
            self.visit(n)

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
        retType = self._typesMap[node.returns.id]
        argsType = []

        for a in node.args.args:
            argsType.append(self._typesMap[a.annotation.id])

        ftype = ir.FunctionType(retType, argsType)
        func = ir.Function(self._module, ftype, name=node.name)
        self._functionMap[node.name] = func

    def visitFunctionDef(self, node):
        self._createFunctionType(node)
        self._visitFunctionBody(node)

    def visitReturn(self, node):
        self._builder.ret(self.visit(node.value))

    def visitConstant(self, node):
        # create a constant.
        typ = self._typesMap[str(type(node.value).__name__)]
        return ir.Constant(typ, node.value)

    def visitName(self, node):
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
        """
        pass

if __name__ == "__main__":
    with open("./toto.py") as f:
        content = f.read()

    root = ast.parse(content)
    t = Translator(True)
    t.visit(root)
    module = t._module
    builder = t._builder

    ftype = ir.FunctionType(ir.IntType(64), [])
    main = ir.Function(module, ftype, name='main')
    bb = main.append_basic_block()

    builder.position_at_end(bb)
    ret = builder.call(t._functionMap['func'], [])

    builder.ret(ret)

    print(module)
