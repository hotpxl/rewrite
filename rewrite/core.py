#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import ast
import types
import inspect
import functools


def rewrite(**kwargs):
    def wrap(func):
        if len(kwargs) == 0:
            return func
        source_code = inspect.getsource(func)

        class Visitor(ast.NodeTransformer):
            def visit_Call(self, node):
                # if isinstance(node.func, ast.Name):
                #     print(node.func.id, node.func.ctx)
                # else:
                #     print(node.func.value, node.func.attr, node.func.ctx)
                # print(' ' + str(node.args))
                for i in ast.iter_child_nodes(node):
                    self.visit(i)
                node.args.insert(0, node.func)
                node.func = ast.Name(id='__call_hook', ctx=ast.Load())
                return node

        func_ast = ast.parse(source_code, mode='exec')
        for i in func_ast.body[0].body:
            Visitor().visit(i)
        for index, i in enumerate(func_ast.body[0].decorator_list):
            if isinstance(i, ast.Call) and isinstance(
                    i.func, ast.Attribute) and i.func.attr == 'rewrite':
                del func_ast.body[0].decorator_list[index]
                break
        func_ast.body[0].name += 'ak'
        n = func_ast.body[0].name
        ast.fix_missing_locations(func_ast)
        print(ast.dump(func_ast))
        g = func.__globals__
        g['__call_hook'] = kwargs['call_hook']
        exec(compile(func_ast, filename='<ast>', mode='exec'), g)
        return g[n]

    return wrap
