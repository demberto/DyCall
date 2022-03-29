#!/usr/bin/env python3

"""
dycall.demangler
~~~~~~~~~~~~~~~~

Contains `DemanglerWindow`.
"""

import logging

import ttkbootstrap as tk
from ttkbootstrap import ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.localization import MessageCatalog as MsgCat

from dycall.util import CopyButton, DemangleError, demangle

log = logging.getLogger(__name__)


class DemanglerWindow(tk.Toplevel):
    """A C++ symbol name demangler utility.

    Found under **Tools** -> **Demangler** in the top menu.
    Uses `dycall.util.demangle` to demangle the name.

    TODO: Syntax highlighted demangled name using Pygments.
    """

    def __init__(self, _: tk.Window):
        log.debug("Initialising")
        self.mangled_name = mangled_name = tk.StringVar()
        self.demangled_name = demangled_name = tk.StringVar()

        super().__init__(title="Demangler", toolwindow=True)
        self.withdraw()
        self.minsize(300, 100)
        self.resizable(True, False)
        self.geometry("500x100")

        self.columnconfigure(0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2)
        self.rowconfigure(0, minsize=45, weight=1)
        self.rowconfigure(1, minsize=45, weight=1)

        self.ml = ml = ttk.Label(self, text=MsgCat.translate("Name"))
        self.me = me = ttk.Entry(self, textvariable=mangled_name)
        self.mb = mb = ttk.Button(
            self, text="Demangle", command=self.demangle, state="disabled"
        )
        self.dl = dl = ttk.Label(self, text="Demangled")
        self.de = de = ttk.Entry(
            self, textvariable=demangled_name, state="readonly", font="TkFixedFont"
        )
        self.db = db = CopyButton(self, demangled_name, state="disabled")

        # https://www.tutorialspoint.com/how-do-i-get-an-event-callback-when-a-tkinter-entry-widget-is-modified
        mangled_name.trace_add("write", self.set_state)

        ml.grid(row=0, column=0, padx=5, pady=10, sticky="w")
        me.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        mb.grid(row=0, column=2, padx=5, pady=10, sticky="w")
        dl.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="w")
        de.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="ew")
        db.grid(row=1, column=2, padx=5, pady=(0, 10), sticky="w")

        self.place_window_center()
        self.deiconify()
        self.focus_set()
        log.debug("Initialised")

    def set_state(self, *_):
        """Toggles the state of the **Demangle** button based on **Name**."""
        if self.me.get():
            self.mb.configure(state="normal")
        else:
            self.mb.configure(state="disabled")

    def demangle(self):
        """Tries to demangle **Name** and update the **Demangled** entry."""
        mangled = self.mangled_name.get()
        try:
            d = demangle(mangled)
        except DemangleError as exc:
            log.exception(exc)
            Messagebox.show_error(
                f"Failed to demangle '{mangled}'", "Demangling Failed"
            )
        else:
            self.demangled_name.set(d)
            self.db.configure(state="normal")
