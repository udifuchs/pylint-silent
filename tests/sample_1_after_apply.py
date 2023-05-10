# pylint: disable=missing-module-docstring
import os  # pylint: disable=unused-import
import sys  # pylint: disable=unused-import
# pylint: disable=unused-import
import time
# pylint: enable=unused-import


def func(name):  # pylint: disable=missing-function-docstring,unused-argument
    try:
        # pylint: disable=exec-used
        exec("1 + 1")
        # pylint: enable=exec-used
        val = eval("2 + 2")  # pylint: disable=eval-used,unused-variable
    except BaseException:  # pylint: disable=broad-exception-caught
        pass

    global VAR  # pylint: disable=global-variable-not-assigned
