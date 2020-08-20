# This is not how you are suppose to document a module.
import os
import sys

def func(name):
    try:
        exec("1 + 1")
        val =eval("2+ 2")
    except BaseException:
        pass

    global VAR
