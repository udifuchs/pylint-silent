#!/usr/bin/python3
# Test code that triggers some pylint messages that need to be disabled.
import os
import sys
# pylint: disable=unused-import
import time
# pylint: enable=unused-import


def func(name):
    try:
        # pylint: disable=exec-used
        exec("1 + 1")
        # pylint: enable=exec-used
        val = eval("2 + 2")
    except BaseException:
        pass

    global VAR
