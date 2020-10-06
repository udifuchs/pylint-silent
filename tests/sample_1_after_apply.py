# pylint: disable=missing-module-docstring
import os  # pylint: disable=unused-import
import sys  # pylint: disable=unused-import

def func(name):  # pylint: disable=missing-function-docstring,unused-argument
    try:
        exec("1 + 1")  # pylint: disable=exec-used
        val = eval("2 + 2")  # pylint: disable=eval-used,unused-variable
    except BaseException:  # pylint: disable=broad-except
        pass

    global VAR  # pylint: disable=global-variable-not-assigned
