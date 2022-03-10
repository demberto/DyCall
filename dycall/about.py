# -*- coding: utf-8 -*-
import logging
import webbrowser

import ttkbootstrap as tk
from ttkbootstrap import ttk
from ttkbootstrap.localization import MessageCatalog as MsgCat

from dycall.util import get_png

log = logging.getLogger(__name__)


class AboutWindow(tk.Toplevel):
    def __init__(self, parent):
        log.debug("Initialising")
        self.parent = parent

        super().__init__(
            alpha=0.95,
            title="About",
            topmost=True,
            overrideredirect=True,
        )
        self.withdraw()
        self.resizable(False, False)
        self.bind("<Escape>", lambda *_: self.destroy())

        tf = ttk.Frame(self)
        self.cb = cb = ttk.Button(tf, text="🗙", command=lambda *_: self.destroy())
        cb.bind(
            "<Enter>",
            lambda *_: self.after(50, lambda: cb.configure(bootstyle="danger")),
        )
        cb.bind(
            "<Leave>",
            lambda *_: self.after(50, lambda: cb.configure(bootstyle="primary")),
        )
        cb.pack(side="right")
        tf.bind("<ButtonPress-1>", self.start_move)
        tf.bind("<ButtonRelease-1>", self.stop_move)
        tf.bind("<B1-Motion>", self.do_move)
        tf.pack(side="top", fill="x")

        ttk.Label(self, text="DyCall", font=tk.font.Font(size=24)).place(
            relx=0.5, rely=0.3, anchor="center"
        )
        ttk.Label(self, text="(c) demberto 2022").place(
            relx=0.5, rely=0.5, anchor="center"
        )

        # https://stackoverflow.com/a/15216402
        self.__github = get_png("github.png")
        gb = ttk.Label(self, image=self.__github, cursor="hand2")

        # https://stackoverflow.com/a/68306781
        gb.bind(
            "<ButtonRelease-1>",
            lambda *_: webbrowser.open_new_tab("https://github.com/demberto/DyCall"),
        )
        gb.place(relx=0.5, rely=0.75, anchor="center")
        ll = ttk.Label(
            self,
            text=MsgCat.translate("DyCall is distributed under the MIT license"),
            font=tk.font.Font(size=9),
        )
        ll.place(relx=0.5, rely=1, anchor="s")

        width = ll.winfo_reqwidth()  # Different languages, different sizes
        self.geometry(f"{width}x200")
        self.place_window_center()
        self.deiconify()
        self.focus_set()
        log.debug("Initalised")

    def start_move(self, event):
        # pylint: disable=attribute-defined-outside-init
        self.x = event.x
        self.y = event.y

    def stop_move(self, _):
        # pylint: disable=attribute-defined-outside-init
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
