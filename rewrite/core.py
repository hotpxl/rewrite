#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import ast
import types
import inspect
import functools

_reentrance = False


def rewrite(**rewrite_kwargs):
    def wrap(func):
        global _reentrance
        if _reentrance:
            return func
        _reentrance = True
        source_code = inspect.getsource(func)
        global_namespace = func.__globals__.copy()
        func_ast = ast.parse(source_code, mode='exec')
        func_ast.body[0].name += '_rewritten'
        new_name = func_ast.body[0].name

        if 'call_advice' in rewrite_kwargs:
            global_namespace['__call_advice'] = rewrite_kwargs['call_advice']

            class Visitor(ast.NodeTransformer):
                def visit_Call(self, node):
                    for i in ast.iter_child_nodes(node):
                        self.visit(i)
                    node.args.insert(0, node.func)
                    node.args.insert(1, ast.Num(node.lineno))
                    node.args.insert(2, ast.Num(node.col_offset))
                    node.func = ast.Name(id='__call_advice', ctx=ast.Load())
                    return node

            for i in func_ast.body[0].body:
                Visitor().visit(i)
        ast.fix_missing_locations(func_ast)
        # print(ast.dump(func_ast))
        exec(
            compile(func_ast, filename='<ast>', mode='exec'), global_namespace)

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            global _reentrance
            _reentrance = True
            nonlocal func_ast
            ret = global_namespace[new_name](*args, **kwargs)
            if 'post_function_hook' in rewrite_kwargs:
                new_ast = rewrite_kwargs['post_function_hook'](func_ast)
                if new_ast is not None:
                    func_ast = new_ast
                    exec(
                        compile(func_ast, filename='<ast>', mode='exec'),
                        global_namespace)
            _reentrance = False
            return ret

        _reentrance = False
        return wrapped_func

    return wrap
