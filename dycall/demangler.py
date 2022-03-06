# -*- coding: utf-8 -*-
import logging

import ttkbootstrap as tk
from ttkbootstrap import ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.localization import MessageCatalog as MsgCat

from dycall.util import (
    CopyButton,
    DemangleError,
    PlatformUnsupportedError,
    demangle,
    set_app_icon,
)

log = logging.getLogger(__name__)


class DemanglerWindow(tk.Toplevel):
    def __init__(self, parent: tk.Window):
        log.debug("Initialising")
        self.parent = parent
        self.mangled_name = mangled_var = tk.StringVar()
        self.demangled_name = demangled_var = tk.StringVar()

        super().__init__(title="Demangler")
        self.withdraw()
        set_app_icon(self)
        self.minsize(300, 100)
        self.geometry("500x100")

        self.columnconfigure(0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2)
        self.rowconfigure(0, minsize=45, weight=1)
        self.rowconfigure(1, minsize=45, weight=1)

        self.ml = ml = ttk.Label(self, text=MsgCat.translate("Name"))
        self.me = me = ttk.Entry(self, textvariable=mangled_var)
        self.mb = mb = ttk.Button(self, text="Demangle", command=self.demangle)
        self.dl = dl = ttk.Label(self, text="Demangled")
        self.de = de = ttk.Entry(self, textvariable=demangled_var, state="readonly")
        self.db = db = CopyButton(self, demangled_var, state="disabled")

        ml.grid(row=0, column=0, padx=5, pady=10, sticky="w")
        me.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        mb.grid(row=0, column=2, padx=5, pady=10, sticky="w")
        dl.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="w")
        de.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="ew")
        db.grid(row=1, column=2, padx=5, pady=(0, 10), sticky="w")

        self.deiconify()
        log.debug("Initialised")

    def demangle(self):
        mangled = self.mangled_name.get()
        try:
            d = demangle(mangled)
        except DemangleError as exc:
            log.exception(exc)
            Messagebox.show_error(
                f"Failed to demangle '{mangled}'", "Demangling Failed"
            )
        except PlatformUnsupportedError as exc:
            log.exception(exc)
            Messagebox.show_error(
                "Demangling is not supported on this platform", "Unsupported Platform"
            )
        else:
            self.demangled_name.set(d)
            self.db.configure(state="normal")
