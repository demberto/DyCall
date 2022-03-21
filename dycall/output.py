# -*- coding: utf-8 -*-
import logging

import ttkbootstrap as tk
from ttkbootstrap import ttk
from ttkbootstrap.localization import MessageCatalog as MsgCat

from dycall.util import CopyButton

log = logging.getLogger(__name__)


class OutputFrame(ttk.Labelframe):
    def __init__(self, _: tk.Window, output: tk.StringVar, exc_type: tk.StringVar):
        log.debug("Initialising")
        title = MsgCat.translate("Output")
        super().__init__(text=title)
        self.event_add("<<OutputSuccess>>", "None")
        self.event_add("<<OutputException>>", "None")
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
