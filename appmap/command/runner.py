import argparse
import getopt
import os
import sys
import textwrap

_parser = argparse.ArgumentParser(
    description=textwrap.dedent("""
Enable recording of the provided command, optionally specifying the
type(s) of recording to enable and disable. If a recording type is
specified as both enabled and disabled, it will be enabled.

This command sets the environment variables described here:
https://appmap.io/docs/reference/appmap-python.html#controlling-recording.
For any recording type that is not explicitly specified, the
corresponding environment variable will not be set.

If no command is provided, the computed set of environment variables
will be displayed.
    """),
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

_RECORDING_TYPES = set(
    [
        "process",
        "remote",
        "requests",
        "tests",
    ]
)


def recording_types(v: str):
    values = set(v.split(","))
    if not values & _RECORDING_TYPES:
        raise argparse.ArgumentTypeError(v)
    return values


_parser.add_argument(
    "--record",
    help="recording types to enable",
    metavar=",".join(_RECORDING_TYPES),
    type=recording_types,
    default=argparse.SUPPRESS,
)
_parser.add_argument(
    "--no-record",
    help="recording types to disable",
    metavar=",".join(_RECORDING_TYPES),
    type=recording_types,
    default=argparse.SUPPRESS,
)

if sys.version_info >= (3, 9):
    _parser.add_argument(
        "--enable-log",
        help="create a log file",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
else:
    # You can see why BooleanOptionalAction was added. This is close, though not
    # really as good....
    _enable_log_group = _parser.add_mutually_exclusive_group()
    _enable_log_group.add_argument(
        "--enable-log",
        help="create a log file",
        dest="enable_log",
        action="store_true",
    )
    _enable_log_group.add_argument(
        "--no-enable-log",
        help="don't create a log file",
        dest="enable_log",
        action="store_false",
    )

_parser.add_argument(
    "command",
    nargs="*",
    help="the command to run (default: display the environment variables)",
    default=argparse.SUPPRESS,
)


def run():
    if len(sys.argv) == 1:
        _parser.print_help()
        sys.exit(1)

    # Use gnu_getopt to separate the command line into args we know about,
    # followed by the command to run (and its args)
    try:
        getopt_flags = ["help", "record=", "no-record=", "enable-log", "no-enable-log"]
        opts, cmd = getopt.gnu_getopt(sys.argv[1:], "+h", getopt_flags)
    except getopt.GetoptError as exc:
        print(exc, file=sys.stderr)
        _parser.print_help()
        sys.exit(1)

    # parse the args after flattening the tuples returned from gnu_getopt
    flags = [f for opt in opts for f in opt if len(f) > 0]
    parsed_args = _parser.parse_args(flags)
    parsed_args = vars(parsed_args)

    # our settings override those in the environment
    envvars = {
        "APPMAP": "true",
        "_APPMAP": "true",
    }

    # Set the environment variables based on the the flags. A recording type in
    # --record overrides one set in --no-record. The environment variable for a
    # type that doesn't appear in either will be unset.
    record = parsed_args.get("record", set())
    no_record = parsed_args.get("no_record", set()) - record
    for enabled in record:
        envvars[f"APPMAP_RECORD_{enabled.upper()}"] = "true"
    for disabled in no_record:
        envvars[f"APPMAP_RECORD_{disabled.upper()}"] = "false"

    envvars["APPMAP_DISABLE_LOG_FILE"] = (
        "true" if parsed_args.get("no_enable_log", set()) else "false"
    )

    if len(cmd) == 0:
        for k, v in sorted(envvars.items()):
            print(f"{k}={v}")
        sys.exit(0)

    os.execvpe(cmd[0], cmd, {**os.environ, **envvars})


if __name__ == "__main__":
    run()
