#!/usr/bin/env python3

"""
dycall.__main__
~~~~~~~~~~~~~~~

Entry point. Command line arguments are parsed and passed over to `App`.
"""

import argparse
import logging
import platform

import desktop_app
import lief

from dycall.app import App
from dycall.types import CALL_CONVENTIONS, PARAMETER_TYPES
from dycall.util import LCIDS

desktop_app.set_process_appid("dycall")
is_windows = platform.system() == "Windows"


# https://stackoverflow.com/a/18700817
def positive_int(s: str) -> int:
    """Positive integer validator for `argparse.ArgumentParser`."""
    i = int(s)
    if i < 0:
        raise argparse.ArgumentTypeError("A positive number is required")
    return i


def main():
    """Arguments are parsed here and passed as keyword arguments."""
    # * Don't use default values for string arguments
    ap = argparse.ArgumentParser(
        prog="DyCall",
        description="Run exported symbols from native libraries",
    )
    ap.add_argument("--log", help="Display logs", action="store_true")
    ap.add_argument("--lib", help="Path/name of library to load on startup.")
    ap.add_argument("--exp", help="Name of export to select from lib.")
    if is_windows:
        ap.add_argument(
            "--conv", help="Calling convention to use.", choices=CALL_CONVENTIONS
        )
    ap.add_argument(
        "--ret", help="Return type of the function.", choices=PARAMETER_TYPES
    )
    ap.add_argument(
        "--rows",
        default=0,
        help="Number of empty rows to create in arguments table",
        type=positive_int,
    )
    ap.add_argument("--lang", help="The language used by the interface", choices=LCIDS)
    ap.add_argument("--out-mode", help="Use 'out' mode", action="store_true")
    ap.add_argument(
        "--hide-errno", help="Hides errno from the status bar", action="store_true"
    )
    ap.add_argument(
        "--no-images",
        action="store_true",
        help="Run without showing any images in the UI.",
    )
    if is_windows:
        ap.add_argument(
            "--hide-gle",
            help="Hides GetLastError from the status bar",
            action="store_true",
        )

    args = ap.parse_args()
    if args.log:
        logging.basicConfig(level=logging.DEBUG)
    else:
        lief.logging.disable()

    launch_args = vars(args)
    _ = launch_args.pop("log", None)  # Logging is handled hee itself
    App(**launch_args).mainloop()


if __name__ == "__main__":
    main()
