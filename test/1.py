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


def haha(f, *args, **kwargs):
    print('in haha', f)
    return f(*args, **kwargs)


def hhh2(a):
    a.body[0].body[0].value.args[1].s = 'new hhh'
    # AST merge
    return a


@other_stuff
@rewrite.rewrite(call_advice=haha, post_function_hook=hhh2)
def func1():
    print('hhh')
    #segment start
    c = some_other(3)
    a = np.random.normal(size=(3, 3))
    b = a * 20
    #segment end
    if b.sum() > 0:
        print('>0')
        # start
        #
        # end
    else:
        print('<=0')
    return b


print(func1())
print(func1())

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
