"""This sample has some comments on lines to be reset!"""
import os
import sys
# pylint: disable=unused-import
import time
# pylint: enable=unused-import

import a_module_unknown_to_pylint  # pylint: disable=import-error # pants: no-infer-dep


def func(name):
    try:
        # pylint: disable=exec-used
        exec("1 + 1")
        # pylint: enable=exec-used
        val = eval("2 + 2")
    except BaseException:
        pass

    foo: int = 'foo'  # pylint: disable=unused-variable,disallowed-name # noqa
    bar: int = 'bar'  # noqa # pylint: disable=unused-variable,disallowed-name

    10 / 0  # pylint: disable=pointless-statement # Dividing by zero is fun

    global VAR
