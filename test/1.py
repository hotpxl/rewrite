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
    return func


def some_other(func):
    return func


def haha(f, *args, **kwargs):
    print('in haha')
    print(f)
    print('done')


# @other_stuff
@rewrite.rewrite(call_hook=123)
def func1():
    print('hhh')
    c = some_other(3)
    a = np.random.normal(size=(3, 3))
    b = a * 20
    return b


print('call')
print(func1())

# @rewrite.rewrite(call_hook=123)
# @some_other
# def do_something():
#     if a.sum() > 0:
#         b = a + 100
#         c = b.dot(b.T)
#         b = mx.nd.add(c, b)
#     else:
#         b = a * 100
#     return b
