#!/usr/bin/python3
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines
# pylint: disable=invalid-name; silent invalid module name
# pylint: enable=invalid-name; silent
# Test code that triggers some pylint messages that need to be disabled.
import os  # pylint: disable=unused-import
import sys  # pylint: disable=unused-import
# pylint: disable=unused-import
import time
# pylint: enable=unused-import


# pylint: disable-next=missing-function-docstring,unused-argument
def func(name):
    try:
        # pylint: disable=exec-used
        exec("1 + 1")
        # pylint: enable=exec-used
        # pylint: disable-next=eval-used,unused-variable
        val = eval("2 + 2")
    except BaseException:  # pylint: disable=broad-exception-caught
        pass

    global VAR  # pylint: disable=global-variable-not-assigned
