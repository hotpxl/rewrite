#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import sys
sys.path.append('../')
import rewrite
import numpy as np


def other_stuff(func):
    def wrapped_fn():
        return func()

    return wrapped_fn


def some_other(func):
    return func


def haha(f, lineno, col_offset, *args, **kwargs):
    print('in haha', f, lineno, col_offset)
    return f(*args, **kwargs)


def hhh2(a):
    a.body[0].body[0].value.args[1].s = 'new hhh'
    # AST merge
    return a


def display_function(func):
    print('>', func, type(func))
    return func


@other_stuff
@rewrite.rewrite(function_advice=display_function)
def func1():
    b=0
    b = b + 1
    return b


def kk():
    print('kk')


func1()

# class AA():
#     @rewrite.rewrite(call_advice=haha)
#     def ak(self, h):
#         print(h)
#
# AA().ak(23)

# @rewrite.rewrite(call_advice=123)
# @some_other
# def do_something():
#     if a.sum() > 0:
#         b = a + 100
#         c = b.dot(b.T)
#         b = mx.nd.add(c, b)
#     else:
#         b = a * 100
#     return b
