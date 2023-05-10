"""Main entry point for pylint-silent."""
import sys
import argparse
import pylint_silent

SIGNATURE = "; silent"

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
    parser.add_argument("signature", default=False, action='store_true')
    args = parser.parse_args()

    signature = SIGNATURE if args.signature else ''
    if args.command == "apply":
        pylint_logfile = args.filename[0]
        pylint_silent.apply(pylint_logfile, signature)
        return 0

    if args.command == "reset":
        for py_filename in args.filename:
            pylint_silent.reset(py_filename, signature, used_signature=args.signature)
        return 0

    if args.command == "stats":
        pylint_silent.statistics(args.filename, signature)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
