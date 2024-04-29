"""Add "# pylint: disable" comments to silence the output of pylint."""
import os
import shutil
from typing import Dict, List, Set

VERSION = "1.4.1"

EPILOG = """
Commands:
  apply <pylint-output-file>
      Add pylint comments based on the output of pylint.
  reset <python-file> ...
      Remove pylint comments from specified python files.
  stats <python-file> ...
      Report statistics on number of pylint comments in specified files.

WARNING:
  Python files are modified in place.
  It is assumed that you are using some version control system.
"""

EOL = "\n"
TEMP_FILE_ENDING = ".created_by_pylint_silent"


def pyfile_add_comments(  # pylint: disable=too-many-locals; silent
    py_filename: str,
    messages: Dict[int, Set[str]],
    signature: str,
    max_line_length: int,
) -> None:
    """Add comments to a python file to silent 'messages'."""
    out_filename = py_filename + TEMP_FILE_ENDING

    with open(py_filename, "r", encoding="utf-8") as py_file, \
         open(out_filename, "w", encoding="utf-8") as out_file:

        for line_no, line in enumerate(py_file):
            if line_no == 0 and line.startswith("#!"):
                # Write shebang before anything else.
                out_file.write(line)

            pylint_line_no = line_no + 1
            if pylint_line_no in messages:
                for module_message in (
                    "missing-module-docstring",
                    "too-many-lines",
                ):
                    # Module level messages require a special treatment
                    # since they do not work with 'disable-next'.
                    if module_message in messages[pylint_line_no]:
                        first_line = (
                            f"# pylint: disable={module_message}{signature}{EOL}"
                        )
                        out_file.write(first_line)
                        messages[pylint_line_no].remove(module_message)

                if "invalid-MODULE-name" in messages[pylint_line_no]:
                    # This is an "invalid-name" module level message.
                    # Adding the 'silent' signature so we can remove it during reset.
                    # The signature has to be hardcoded to be able to remove it.
                    first_line = (
                        "# pylint: disable=invalid-name; silent invalid module name"
                        + EOL
                    )
                    out_file.write(first_line)
                    # Next we need to re-enable the "invalid-name" message for
                    # the rest of the file.
                    first_line = f"# pylint: enable=invalid-name; silent{EOL}"
                    out_file.write(first_line)
                    messages[pylint_line_no].remove("invalid-MODULE-name")

                # Sort messages alphabetically for reproducible output.
                msg_str = ",".join(sorted(messages[pylint_line_no]))
                if msg_str:
                    new_line = (
                        f"{line.rstrip()}  # pylint: disable={msg_str}{signature}{EOL}"
                    )
                    if len(new_line) <= max_line_length:
                        line = new_line
                    else:
                        indent_pos = len(line) - len(line.lstrip(" \t"))
                        indent = line[:indent_pos]
                        new_line = (
                            f"{indent}# pylint: disable-next={msg_str}{signature}{EOL}"
                        )
                        out_file.write(new_line)
            if line_no == 0 and line.startswith("#!"):
                continue  # Shebang line already written.
            out_file.write(line)

    shutil.copymode(py_filename, out_filename)
    os.rename(out_filename, py_filename)


def apply(pylint_logfile: str, signature: str, max_line_length: int) -> None:
    """Process the output of pylint add disable comments for all messages."""
    active_py_filename = None
    messages: Dict[int, Set[str]] = {}

    with open(pylint_logfile, "r", encoding="utf-8") as logfile:

        for line in logfile:
            # 'line' should look like this:
            # "test.py:35:10: W0613: Unused argument 'name' (unused-argument)"
            line_parts = line.split(":", maxsplit=4)

            if len(line_parts) != 5:
                # Ignore lines with a different format.
                continue

            py_filename = line_parts[0]
            line_no = int(line_parts[1])
            # line_pos = line_parts[2]
            code = line_parts[3]
            message = line_parts[4]

            if code in {
                    " R0401",  # Cyclic import
                    " R0801",  # Similar lines in 2 files
            }:
                # Pylint reports the wrong file and line number for these messages.
                continue
            if code == " C0326":
                # For C0326 the message symbol is shown on the next line.
                # In pylint 2.6 bad-whitespace message was removed.
                message_symbol = "bad-whitespace"  # pragma: no cover
            else:
                if message.find("(") < 0:  # pragma: no cover
                    print("Message missing message symbol:", message)
                    continue
                message_symbol = message[message.rfind("(") + 1:message.rfind(")")]
                if message_symbol == "invalid-name" and "Module name" in message:
                    # pylint reported a message of the form:
                    # C0103: Module name "{}" doesn't conform to {} naming style
                    # Give it a unique symbol since it requires special treatment.
                    message_symbol = "invalid-MODULE-name"

            if py_filename != active_py_filename:
                # New file. Finish processing previous file.
                if active_py_filename is not None:
                    pyfile_add_comments(  # pragma: no cover
                        active_py_filename, messages, signature, max_line_length
                    )
                active_py_filename = py_filename
                messages = {}

            if line_no in messages:
                messages[line_no].add(message_symbol)
            else:
                # First message for this line_no
                messages[line_no] = {message_symbol}

        # Handle last file.
        if active_py_filename is not None:
            pyfile_add_comments(
                active_py_filename, messages, signature, max_line_length
            )


def reset(py_filename: str, signature: str) -> None:
    """Remove all pylint comments from a python file."""
    out_filename = py_filename + TEMP_FILE_ENDING
    something_changed = False

    with open(py_filename, "r", encoding="utf-8") as py_file, \
         open(out_filename, "w", encoding="utf-8") as out_file:

        for line in py_file:
            if line.rstrip() in {
                f"# pylint: disable=missing-module-docstring{signature}",
                f"# pylint: disable=too-many-lines{signature}",
                "# pylint: disable=invalid-name; silent invalid module name",
                "# pylint: enable=invalid-name; silent",
            }:
                something_changed = True
                continue
            if "# pylint: disable-next=" in line:
                something_changed = True
                continue

            # Do not remove comments that weren't generated by pylint-silent
            # (if --signature)
            if signature and signature not in line:
                out_file.write(line)
                continue

            comment_pos = line.lstrip().find("# pylint: disable=")
            # Do not remove comments starting at beginning of line
            if comment_pos > 0:
                comment_pos = line.find("# pylint: disable=")
                stripped_line = line[:comment_pos].rstrip()

                # Other tooling comments may follow pylint comments
                # Make sure to add *back* that comment before proceeding
                other_comment_pos = line.find("#", comment_pos + 1)
                if other_comment_pos > 0:
                    stripped_line += "  " + line[other_comment_pos:].rstrip()
                line = stripped_line + EOL
                something_changed = True
            out_file.write(line)

    if something_changed:
        shutil.copymode(py_filename, out_filename)
        os.rename(out_filename, py_filename)
    else:
        os.remove(out_filename)


def statistics(py_filenames: List[str], signature: str) -> None:
    """Show statistics on pylint comments from a list of python files."""
    stats: Dict[str, int] = {}

    for py_filename in py_filenames:

        with open(py_filename, "r", encoding="utf-8") as py_file:

            for line in py_file:
                # when signature is used, only collect comments with it
                if signature and signature not in line:
                    continue

                comment_pos = line.lstrip().find("# pylint: disable")
                # Ignore comments starting at beginning of line
                if (
                    comment_pos > 0
                    or line.lstrip().startswith("# pylint: disable-next=")
                    or line.rstrip() in {
                        f"# pylint: disable=missing-module-docstring{signature}",
                        f"# pylint: disable=too-many-lines{signature}",
                        "# pylint: disable=invalid-name; silent invalid module name",
                    }
                ):
                    comment = line.lstrip()[comment_pos:].rstrip()

                    # Other tooling comments may follow pylint comments
                    other_comment_pos = comment.find("#", 1)
                    if other_comment_pos > 0:
                        comment = comment[:other_comment_pos].rstrip()

                    if comment.endswith("; silent"):
                        comment = comment[:comment.find("; silent")]
                    # 'comment' may disable several messages:
                    # "# pylint: disable=too-many-branches,too-many-statements"
                    messages = comment[comment.rfind("=") + 1:].split(";")[0].split(",")
                    for message in messages:
                        if message in stats:
                            stats[message] += 1
                        else:
                            stats[message] = 1

    for message in sorted(stats):
        print(f"{message}: {stats[message]}")

    print("TOTAL:", sum(stats.values()))
