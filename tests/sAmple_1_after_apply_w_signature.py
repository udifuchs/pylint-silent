#!/usr/bin/python3
# pylint: disable=missing-module-docstring; silent
# pylint: disable=too-many-lines; silent
# pylint: disable=invalid-name; silent invalid module name
# pylint: enable=invalid-name; silent
# Test code that triggers some pylint messages that need to be disabled.
import os  # pylint: disable=unused-import; silent
import sys  # pylint: disable=unused-import; silent
# pylint: disable=unused-import
import time
# pylint: enable=unused-import


def func(name):  # pylint: disable=missing-function-docstring,unused-argument; silent
    try:
        # pylint: disable=exec-used
        exec("1 + 1")
        # pylint: enable=exec-used
        val = eval("2 + 2")  # pylint: disable=eval-used,unused-variable; silent
    except BaseException:  # pylint: disable=broad-exception-caught; silent
        pass

    global VAR  # pylint: disable=global-variable-not-assigned; silent
