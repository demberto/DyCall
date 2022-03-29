#!/usr/bin/env python3

"""
dycall.output
~~~~~~~~~~~~~

Contains `OutputFrame`.
"""

import logging

import ttkbootstrap as tk
from ttkbootstrap import ttk
from ttkbootstrap.localization import MessageCatalog as MsgCat

from dycall.util import CopyButton

log = logging.getLogger(__name__)


class OutputFrame(ttk.Labelframe):
    """Shows the value returned/exception caused by calling the exported function.

    Contains a readonly `Entry` to display text and a copy button alongside.
    """

    def __init__(self, _: tk.Window, output: tk.StringVar, exc_type: tk.StringVar):
        log.debug("Initialising")
        title = MsgCat.translate("Output")
        super().__init__(text=title)
        self.bind_all("<<OutputSuccess>>", lambda *_: self.configure(text=title))
        self.bind_all(
            "<<OutputException>>", lambda _: self.configure(text=exc_type.get())
        )
        self.oe = oe = ttk.Entry(
            self,
            font="TkFixedFont",
            state="readonly",
            textvariable=output,
        )
        self.oc = oc = CopyButton(self, output, state="disabled")
        oc.pack(side="right", padx=(0, 5), pady=5)
        oe.pack(fill="x", padx=5, pady=5)
        log.debug("Initialised")
