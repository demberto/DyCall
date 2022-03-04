import logging

import ttkbootstrap as tk
from ttkbootstrap import ttk

log = logging.getLogger(__name__)


class StatusBarFrame(ttk.Frame):
    def __init__(self, _: tk.Window, status: tk.StringVar):
        log.debug("Initialising")
        super().__init__()
        self.sb = ttk.Label(self, textvariable=status)
        self.sb.pack(side="left")
        log.debug("Initialised")
