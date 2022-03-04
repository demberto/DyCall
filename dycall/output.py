import logging

import ttkbootstrap as tk
from ttkbootstrap import ttk
from ttkbootstrap.localization import MessageCatalog as MC

from dycall.util import CopyButton

log = logging.getLogger(__name__)


class OutputFrame(ttk.Labelframe):
    def __init__(self, _: tk.Window, output: tk.StringVar):
        super().__init__(text=MC.translate("Output"))
        self.oe = oe = ttk.Entry(
            self,
            font="TkFixedFont",
            state="readonly",
            textvariable=output,
        )
        self.oc = oc = CopyButton(self, output, state="disabled")
        oc.pack(side="right", padx=(0, 5), pady=5)
        oe.pack(fill="x", padx=5, pady=5)
