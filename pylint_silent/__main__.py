"""Main entry point for pylint-silent."""
import sys
import pylint_silent


def main() -> None:
    """Run pylint_silent based on the command line arguments."""
    if len(sys.argv) < 2:
        print(pylint_silent.__doc__)
        return

    if sys.argv[1] == "apply":
        pylint_logfile = sys.argv[2]
        pylint_silent.apply(pylint_logfile)
    elif sys.argv[1] == "reset":
        for py_filename in sys.argv[2:]:
            pylint_silent.reset(py_filename)
    elif sys.argv[1] == "stats":
        pylint_silent.statistics(sys.argv[2:])
    elif sys.argv[1] == "--version":
        print(f"pylint-silent {pylint_silent.__version__}")
    else:
        print(pylint_silent.__doc__)


if __name__ == "__main__":
    main()
