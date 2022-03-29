#!/usr/bin/env python3

"""
dycall.status_bar
~~~~~~~~~~~~~~~~~

Contains `StatusBarFrame`.
"""

import logging
import os
import platform

try:
    import win32api
except ImportError:
    pass

import ttkbootstrap as tk
from ttkbootstrap import ttk

from dycall.util import StaticThemedTooltip

log = logging.getLogger(__name__)


class StatusBarFrame(ttk.Frame):
    """Implements a typical desktop application status bar.

    Contains:
        - A useful message which changes according to the current state of the
          application and user events (on the left).
        - Errno and GetLastError (Window only) on the right.

    Command line arguments:
        - `--hide-errno` to hide **errno**.
        - `--hide-gle` to hide **GetLastError** (Windows only).
    """

    def __init__(
        self,
        _: tk.Window,
        status: tk.StringVar,
        get_last_error: tk.IntVar,
        show_get_last_error: tk.BooleanVar,
        errno: tk.IntVar,
        show_errno: tk.BooleanVar,
    ):
        log.debug("Initialising")
        super().__init__()
        self.__show_get_last_error = show_get_last_error
        self.__show_errno = show_errno
        is_windows = platform.system() == "Windows"

        # Status
        self.sb = sb = ttk.Label(self, textvariable=status)
        sb.pack(side="left")

        # Errcodes
        self.eg = eg = ttk.Frame(self)

        if is_windows:
            # GetLastError
            gf = ttk.Frame(eg)
            ttk.Label(gf, text="GetLastError: ").pack(side="left")
            self.gb = gb = ttk.Label(
                gf, textvariable=get_last_error, font="TkFixedFont"
            )
            gf.bind(
                "<Enter>",
                lambda *_: StaticThemedTooltip(
                    gf, lambda *_: win32api.FormatMessageW(get_last_error.get())
                ),
            )
            self.bind_all(
                "<<ToggleGetLastError>>",
                lambda event: gf.grid_forget()
                if event.state == 0
                else gf.grid_configure(row=0, column=0),
            )
            gb.pack(side="right")
            if show_get_last_error.get():
                gf.grid(row=0, column=0)

            # Separator
            self.__sf = sf = ttk.Frame(eg)
            ttk.Separator(sf, orient="vertical").place(relheight=1.0)
            sf.bind_all("<<ToggleErrno>>", lambda *_: self.adjust_separator(), add=True)
            sf.bind_all(
                "<<ToggleGetLastError>>", lambda *_: self.adjust_separator(), add=True
            )
            if show_get_last_error.get() and show_errno.get():
                sf.grid(row=0, column=1, sticky="NS")

        # Errno
        ef = ttk.Frame(eg)
        ttk.Label(ef, text="errno: ").pack(side="left")
        self.eb = eb = ttk.Label(ef, textvariable=errno, font="TkFixedFont")
        ef.bind(
            "<Enter>",
            lambda *_: StaticThemedTooltip(ef, os.strerror(errno.get())),
        )
        self.bind_all(
            "<<ToggleErrno>>",
            lambda event: ef.grid_forget()
            if event.state == 0
            else ef.grid_configure(row=0, column=2),
            add=True,
        )
        eb.pack(side="right")
        if show_errno.get():
            ef.grid(row=0, column=2)

        eg.pack(side="right", fill="y")
        log.debug("Initialised")

    def adjust_separator(self):
        """Reconfigures separator when **errno** or **GetLastError** is hidden.

        Only used on Windows.
        """
        if self.__show_errno.get() and self.__show_get_last_error.get():
            self.__sf.grid_configure(row=0, column=1, sticky="NS")
        else:
            self.__sf.grid_forget()
