#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import ast
import types
import inspect
import functools


def rewrite(**rewrite_kwargs):
    def wrap(func):
        source_code = inspect.getsource(func)
        global_namespace = func.__globals__.copy()
        func_ast = ast.parse(source_code, mode='exec')
        func_ast.body[0].name += '_rewritten'
        new_name = func_ast.body[0].name

        # Delete the decorator itself. Assume the attribute name is "rewrite".
        for index, i in enumerate(func_ast.body[0].decorator_list):
            if isinstance(i, ast.Call) and isinstance(
                    i.func, ast.Attribute) and i.func.attr == 'rewrite':
                del func_ast.body[0].decorator_list[index]
                break

        if 'call_advice' in rewrite_kwargs:
            global_namespace['__call_advice'] = rewrite_kwargs['call_advice']

            class Visitor(ast.NodeTransformer):
                def visit_Call(self, node):
                    for i in ast.iter_child_nodes(node):
                        self.visit(i)
                    node.args.insert(0, node.func)
                    node.func = ast.Name(id='__call_advice', ctx=ast.Load())
                    return node

            for i in func_ast.body[0].body:
                Visitor().visit(i)
        ast.fix_missing_locations(func_ast)
        exec(
            compile(func_ast, filename='<ast>', mode='exec'), global_namespace)

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            nonlocal func_ast
            ret = global_namespace[new_name](*args, **kwargs)
            if 'post_function_hook' in rewrite_kwargs:
                new_ast = rewrite_kwargs['post_function_hook'](func_ast)
                if new_ast is not None:
                    func_ast = new_ast
                    exec(
                        compile(func_ast, filename='<ast>', mode='exec'),
                        global_namespace)
            return ret

        return wrapped_func

    return wrap
