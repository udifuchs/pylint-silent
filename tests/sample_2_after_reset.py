"""This sample has some comments on lines to be reset!"""
import os
import sys
# pylint: disable=unused-import
import time
# pylint: enable=unused-import

import a_module_unknown_to_pylint  # pants: no-infer-dep


def func(name):
    try:
        # pylint: disable=exec-used
        exec("1 + 1")
        # pylint: enable=exec-used
        val = eval("2 + 2")
    except BaseException:
        pass

    foo: int = 'foo'  # noqa
    bar: int = 'bar'  # noqa

    10 / 0  # Dividing by zero is fun

    global VAR
