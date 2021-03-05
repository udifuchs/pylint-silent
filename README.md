# pylint-silent
**Automatically add code comments to silence the output of [pylint](https://github.com/PyCQA/pylint).**

`pylint` can be very useful in finding software bugs in python code. A good article demonstrating this is [Why Pylint is both useful and unusable, and how you can actually use it](https://pythonspeed.com/articles/pylint/). In short, when running `pylint` on existing code, it tends to output tons of messages.

`pylint-silent` is suppose to make `pylint` usable. The idea is to automatically add code comments of the form `# pylint: disable` to silent every `pylint` message. This will allow you to deploy `pylint` in a Continuous Integration (CI) setup. If a code commit introduces **new** `pylint` messages, these will be visible immediately.

On top of that, all existing `pylint` messages will show up as comments in the code. When you work on a piece of code and see a `pylint` comment, you can try to fix it.

### Install
`pylint-silent` can be installed from [pypi](https://pypi.org/project/pylint-silent/)
```
pip install pylint-silent
```
### Usage
The basic workflow for running `pylint-silent` for the first time is:
```
pylint my_package > pylint.log
pylint-silent apply pylint.log
pylint my_package  # This should return a perfect 10.00 score.
```
**WARNING: `pylint-silent` modifies python files in place.
It is assumed that you are using some version control system.**

For example, if `pylint` produced this message:
```
test.py:35:10: W0613: Unused argument 'name' (unused-argument)
```

`pylint-silent` would add this comment:
```
def func(name):  # pylint: disable=unused-argument
```

For subsequent runs, you probably want to clear the old comments first:
```
pylint-silent reset my_package/*.py  # List all python files here
pylint my_package > pylint.log
pylint-silent apply pylint.log
```

There are two reasons to clear old comments:
1. Remove stale comments to code that was already fixed.
2. `pylint-silent` does not know how to handle lines that already have a `# pylint` comment in them.

### Known limitations
In some cases `pylint-silent` may break your code:
```
FAVICON = base64.decodestring("""  # pylint: disable=deprecated-method
...
```
Luckily, you can now use `pylint` to detect such cases. In this case `pylint` would ignore the comment because it is part of the string. Therefore, the warning message would still show up. This code has to be fixed manually:
```
FAVICON = base64.decodestring(  # pylint: disable=deprecated-method
"""...
```

Another issue is that messages that involve multiple files cannot be silenced. I'm aware of two such messages:

*  cyclic-import
* duplicate-code

You could just disable these messages. Personally I think that these are relevant messages. So instead I just modify `pylint` score calculation to something like:
```
evaluation=10.0 + 0.15 - 10 * ((float(5 * error + warning + refactor + convention) / statement) * 10)
```
The `0.15` artificially raises the score to 10.0 and makes `pylint` return a success code. The factor of `10 *` increases the score sensitivity, which, by default, is way too low even for a medium sized project.

`pylint` also lets you disable a checks on a block of code:
```
# pylint: disable=unused-import                                                         
import time
import sys                                                                             
# pylint: enable=unused-import 
```
`pylint-silent` would ignore these blocks. `pylint-silent reset` would not clear these messages and `pylint-silent stats` would not count them.

### Alternatives

An alternative solution to `pylint` noise is [pylint-ignore](https://pypi.org/project/pylint-ignore/).
Whichever option you choose, I recommend reading their documentation about how `pylint` should be used.

### Summary
`pylint`'s motto is: **It's not just a linter that annoys you!**

`pylint-silent` helps `pylint` live up to its motto.

