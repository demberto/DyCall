#!/usr/bin/env python3

"""
dycall.about
~~~~~~~~~~~~

Contains `AboutWindow`.
"""

from __future__ import annotations

import logging
import webbrowser

import requests

try:
    import importlib.metadata as pkg_metadata
except ImportError:
    import importlib_metadata as pkg_metadata  # type: ignore

import ttkbootstrap as tk
from ttkbootstrap import ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.localization import MessageCatalog as MsgCat

from dycall.util import get_img

log = logging.getLogger(__name__)


class AboutWindow(tk.Toplevel):
    """DyCall's about page.

    Found under **Help** -> **About** in the top menu.
    Only one instance of this can be open at a time due to its
    singleton nature.

    Shows:
    - Name and installed version of package.
    - Copyright.
    - Hyperlink to GitHub repo.
    - Names and installed versions of dependencies.
    - Button to check for an updated version of DyCall.
    - License notice.
    """

    def __init__(self, _: tk.Window, is_opened: tk.BooleanVar):
        log.debug("Initialising")
        self.__is_opened = is_opened

        super().__init__(
            alpha=0.95,
            title="About",
            topmost=True,
            overrideredirect=True,
        )
        self.withdraw()
        self.resizable(False, False)
        self.bind("<Escape>", lambda *_: self.destroy())

        # Topbar to allow window dragging
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

        # Project name and version
        mf = ttk.Frame(self)
        ttk.Label(mf, text="DyCall", font=tk.font.Font(size=24)).pack(side="left")
        ttk.Label(
            mf, text=f"v{pkg_metadata.version('dycall')}", font=tk.font.Font(size=10)
        ).pack(side="right", pady=(10, 0))
        mf.pack(pady=10)

        ttk.Label(self, text="(c) demberto 2022").pack(pady=5)

        # Repo link
        # https://stackoverflow.com/a/15216402
        self.__github_png = get_img("github.png")
        gb = ttk.Label(self, cursor="hand2")
        if self.__github_png:
            gb.configure(image=self.__github_png)
        else:
            # Imageless mode
            gb.configure(text="DyCall @ Github", foreground="green")

        # https://stackoverflow.com/a/68306781
        gb.bind(
            "<ButtonRelease-1>",
            lambda *_: webbrowser.open_new_tab("https://github.com/demberto/DyCall"),
        )
        gb.pack(pady=5)

        # Dependencies
        requirements: list[tuple[str, str]] = []
        for requirement in pkg_metadata.requires("dycall"):  # type: ignore
            package = requirement.split(">")[0]
            try:
                requirements.append((package, pkg_metadata.version(package)))
            except pkg_metadata.PackageNotFoundError:
                pass
        tv = ttk.Treeview(
            self,
            columns=("Package", "Version"),
            show="tree",
            height=len(requirements),
            selectmode="none",
        )
        tv.column("#0", width=0, stretch=False)
        tv.column("Package", width=150)
        tv.column("Version", width=50)
        for package, version in requirements:
            tv.insert("", "end", values=(package, version))
        tv.pack(pady=5, fill="x", padx=5)

        # Update checker
        self.__ubt = tk.StringVar(value=MsgCat.translate("Check for updates"))
        self.__ub = ub = ttk.Button(
            self,
            textvariable=self.__ubt,
            command=lambda *_: self.check_for_updates(),
        )
        ub.pack(pady=10)

        # License notice
        ll = ttk.Label(
            self,
            text=MsgCat.translate("DyCall is distributed under the MIT license"),
            font=tk.font.Font(size=9),
        )
        ll.pack(side="bottom", pady=(0, 5))

        width = max(ll.winfo_reqwidth(), 250)
        self.geometry(f"{width}x410")
        self.place_window_center()
        self.deiconify()
        self.focus_set()
        self.grab_set()
        log.debug("Initialised")

    def destroy(self) -> None:
        """Resets singleton lock and exits."""
        self.__is_opened.set(False)
        return super().destroy()

    def start_move(self, event: tk.tk.Event):
        """Window drag start handler."""
        # pylint: disable=attribute-defined-outside-init
        self.x = event.x
        self.y = event.y

    def stop_move(self, _):
        """Window drag stop handler."""
        # pylint: disable=attribute-defined-outside-init
        self.x = None
        self.y = None

    def do_move(self, event: tk.tk.Event):
        """Window dragging action handler."""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def check_for_updates(self):
        """Synchronous update checker using GitHub API."""

        def reset_button():
            self.__ubt.set(MsgCat.translate("Check for updates"))
            self.__ub.configure(bootstyle="primary")

        self.__ubt.set(MsgCat.translate("Checking..."))
        self.__ub.configure(bootstyle="secondary")
        self.update()
        try:
            r = requests.get(
                "https://api.github.com/repos/demberto/DyCall/releases/latest"
            )
        except requests.exceptions.RequestException as exc:
            reset_button()
            log.exception(exc)
            if (
                Messagebox.retrycancel(
                    f"Failed to check for updates! ({type(exc).__name__}). Retry?",
                    "Update check failed",
                    parent=self,
                )
                == "Retry"
            ):
                self.check_for_updates()
        else:
            reset_button()
            release = r.json()
            installed_version = f"v{pkg_metadata.version('dycall')}"
            latest_version = release["tag_name"]
            if installed_version != latest_version:
                if (
                    Messagebox.show_question(
                        "A new version is available. Open the update page?",
                        "Update available",
                        parent=self,
                    )
                    == "Yes"
                ):
                    webbrowser.open_new_tab(
                        "https://github.com/demberto/DyCall/releases/latest"
                    )
            else:
                Messagebox.show_info(
                    "No new updates are available currently.",
                    "No updates available",
                    parent=self,
                )
