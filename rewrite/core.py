#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import ast
import copy
import types
import inspect
import functools

_reentrance = False

import sys


def evaluate_function_definition(function_ast, global_namespace,
                                 closure_parameters, closure_arguments):
    function_name = function_ast.body[0].name
    evaluation_context = ast.Module(body=[
        ast.FunctionDef(
            name='evaluation_context',
            args=ast.arguments(
                args=[
                    ast.arg(arg=i, annotation=None) for i in closure_parameters
                ],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[]),
            body=[
                function_ast.body[0],
                ast.Return(value=ast.Name(id=function_name, ctx=ast.Load()))
            ],
            decorator_list=[],
            returns=None)
    ])
    ast.fix_missing_locations(evaluation_context)
    local_namespace = {}
    exec(
        compile(evaluation_context, filename='<ast>', mode='exec'),
        global_namespace, local_namespace)
    ret = local_namespace['evaluation_context'](*closure_arguments)
    return ret


def add_type_tracing(function_ast):
    closure_parameters = []
    closure_arguments = []
    closure_parameters.append('__type_tracing')

    nodes = {}
    node_id_counter = 0

    def type_tracing(expr, node_id):
        print('>', expr, type(expr))
        nodes[node_id] = type(expr)
        return expr

    closure_arguments.append(type_tracing)

    class Visitor(ast.NodeTransformer):
        # Do not recurse into inner definitions.
        def visit_FunctionDef(self, node):
            return node

        def visit_AsyncFunctionDef(self, node):
            return node

        def visit_ClassDef(self, node):
            return node

        def visit_BinOp(self, node):
            nonlocal node_id_counter
            for i in ast.iter_child_nodes(node):
                self.visit(i)
            node.left = ast.Call(
                func=ast.Name(id='__type_tracing', ctx=ast.Load()),
                args=[node.left, ast.Num(n=node_id_counter)],
                keywords=[])
            node_id_counter += 1
            node.right = ast.Call(
                func=ast.Name(id='__type_tracing', ctx=ast.Load()),
                args=[node.right, ast.Num(n=node_id_counter)],
                keywords=[])
            node_id_counter += 1
            return node

    for i in function_ast.body[0].body:
        Visitor().visit(i)
    return (function_ast, closure_parameters, closure_arguments)


def rewrite(post_function_hook=None, function_advice=None):
    def wrap(func):
        global _reentrance
        if _reentrance:
            return func
        _reentrance = True
        source_code = inspect.getsource(func)
        function_ast = ast.parse(source_code, mode='exec')

        closure_parameters = []
        closure_arguments = []

        function_ast, i, j = add_type_tracing(function_ast)
        closure_parameters.extend(i)
        closure_arguments.extend(j)

        print(pretty_print(function_ast, include_attributes=False))
        new_function = evaluate_function_definition(
            function_ast, func.__globals__, closure_parameters,
            closure_arguments)

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            global _reentrance
            _reentrance = True
            nonlocal function_ast
            nonlocal new_function
            ret = new_function(*args, **kwargs)
            # if post_function_hook is not None:
            #     new_ast = post_function_hook(function_ast)
            #     if new_ast is not None:
            #         function_ast = new_ast
            #         exec(
            #             compile(function_ast, filename='<ast>', mode='exec'),
            #             global_namespace, local_namespace)
            #         new_function = local_namespace[new_name]
            _reentrance = False
            return ret

        _reentrance = False
        return wrapped_func

    return wrap


def pretty_print(node,
                 annotate_fields=True,
                 include_attributes=False,
                 indent='  '):
    def format(node, level=0):
        if isinstance(node, ast.AST):
            fields = [(i, format(j, level)) for i, j, in ast.iter_fields(node)]
            if include_attributes and node._attributes:
                fields.extend([(i, format(getattr(node, i), level))
                               for i in node._attributes])
            return ''.join([
                type(node).__name__, '(',
                ', '.join(('{}={}'.format(*field) for field in fields)
                          if annotate_fields else (i for _, i in fields)), ')'
            ])
        elif isinstance(node, list):
            lines = [indent * (level + 2) + format(i, level + 2) for i in node]
            if 0 < len(lines):
                return '[\n' + ',\n'.join(lines) + '\n' + indent * (
                    level + 1) + ']'
            else:
                return '[]'
        else:
            return repr(node)

    if not isinstance(node, ast.AST):
        raise TypeError(
            'Expected ast.AST, got {}.'.format(type(node).__name__))
    return format(node)


def copy(function_ast):
    return copy.deepcopy(function_ast)
