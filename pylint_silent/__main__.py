"""Main entry point for pylint-silent."""
import sys
import argparse
import pylint_silent


def main() -> int:
    """Run pylint_silent based on the command line arguments."""
    parser = argparse.ArgumentParser(
        prog="pylint-silent",
        description=pylint_silent.__doc__,
        epilog=pylint_silent.EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    parser.add_argument(
        "--version", action="version", version=f"pylint-silent {pylint_silent.VERSION}"
    )
    parser.add_argument("command", choices=["apply", "reset", "stats"])
    parser.add_argument("filename", nargs="+")
    args = parser.parse_args()

    if args.command == "apply":
        pylint_logfile = args.filename[0]
        pylint_silent.apply(pylint_logfile)
        return 0

    if args.command == "reset":
        for py_filename in args.filename:
            pylint_silent.reset(py_filename)
        return 0

    if args.command == "stats":
        pylint_silent.statistics(args.filename)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
