#!/usr/bin/env python3

"""
dycall.top_menu
~~~~~~~~~~~~~~~

Contains `TopMenu`.
"""

from __future__ import annotations

import collections
import logging
import platform

import ttkbootstrap as tk
from ttkbootstrap.localization import MessageCatalog

from dycall.about import AboutWindow
from dycall.demangler import DemanglerWindow
from dycall.types import SortOrder
from dycall.util import Lang2LCID, LCID2Lang, get_img

log = logging.getLogger(__name__)


class _Menu(tk.Menu):
    def add_cascade(self, label: str, underline: int = 0, **kwargs):
        super().add_cascade(
            label=MessageCatalog.translate(label),
            underline=underline,
            **kwargs,
        )

    def add_command(self, label: str, **kwargs):
        super().add_command(label=MessageCatalog.translate(label), **kwargs)

    def add_checkbutton(self, label: str, **kwargs):
        super().add_checkbutton(label=MessageCatalog.translate(label), **kwargs)

    def add_radiobutton(self, label: str, **kwargs):
        super().add_radiobutton(label=MessageCatalog.translate(label), **kwargs)


class TopMenu(_Menu):
    """DyCall's top menu.

    Hierarchy:
    - File
        - Open Recents
    - Options
        - Language
        - Theme
        - OUT Mode
        - Show GetLastError (Windows only)
        - Show errno
    - View
        - Sort Exports By
            - Name (ascending)
            - Name (descending)
    - Tools
        - Demangler
    - Help
        - About

    `F11` for toggling fullscreen.
    """

    def __init__(
        self,
        root: tk.Window,
        outmode: tk.BooleanVar,
        locale: tk.StringVar,
        sort_order: tk.StringVar,
        show_get_last_error: tk.BooleanVar,
        show_errno: tk.BooleanVar,
        about_opened: tk.BooleanVar,
        theme: tk.StringVar,
        recents: collections.deque,
    ):
        super().__init__()
        self.__root = root
        self.__locale = locale
        self.__about_opened = about_opened
        self.__recents = recents
        self.__lang = tk.StringVar(value=LCID2Lang[locale.get()])

        # File
        self.fo = _Menu()
        self.add_cascade(label="File", menu=self.fo)

        # File -> Open Recent
        self.fop = fop = _Menu()
        self.__clock_png = get_img("clock.png")
        self.fo.add_cascade(
            menu=fop,
            label="Open Recent",
            underline=5,
            image=self.__clock_png,
            compound="left",
        )
        self.bind_all("<<UpdateRecents>>", lambda *_: self.update_recents(True))
        self.update_recents()

        # Options
        self.mo = _Menu()
        self.add_cascade(label="Options", menu=self.mo)

        # Options -> Language
        self.mol = mol = _Menu(self.mo)
        self.__translate_png = get_img("translate.png")
        for lang in LCID2Lang.values():
            mol.add_radiobutton(
                label=lang,
                variable=self.__lang,
                command=self.change_lang,
            )
        self.mo.add_cascade(
            label="Language",
            menu=mol,
            image=self.__translate_png,
            compound="left",
        )

        # Options -> Theme
        self.mot = _Menu(self.mo)
        self.__theme_png = get_img("theme.png")
        for label in ("System", "Light", "Dark"):
            self.mot.add_radiobutton(
                label=label,
                variable=theme,
                command=lambda: root.event_generate("<<ThemeChanged2>>"),
            )
        self.mo.add_cascade(
            label="Theme",
            menu=self.mot,
            image=self.__theme_png,
            compound="left",
        )

        # Options -> OUT mode
        self.mo.add_checkbutton(label="OUT Mode", variable=outmode)

        # Options -> Show GetLastError
        if platform.system() == "Windows":
            mo.add_checkbutton(
                label=MsgCat.translate("Show GetLastError"),
            self.mo.add_checkbutton(
                label="Show GetLastError",
                variable=show_get_last_error,
                command=lambda: root.event_generate(
                    "<<ToggleGetLastError>>", state=int(show_get_last_error.get())
                ),
            )

        # Options -> Show errno
        self.mo.add_checkbutton(
            label="Show errno",
            variable=show_errno,
            command=lambda: root.event_generate(
                "<<ToggleErrno>>", state=int(show_errno.get())
            ),
        )

        # View
        self.vt = _Menu()
        self.add_cascade(label="View", menu=self.vt)

        # View -> Sort Exports By
        self.vse = _Menu()
        self.__sort_png = get_img("sort.png")
        self.__sort_name_asc_png = get_img("sort_name_asc.png")
        self.__sort_name_desc_png = get_img("sort_name_desc.png")
        sorter_imgs = (
            self.__sort_name_asc_png,
            self.__sort_name_desc_png,
        )
        for sorter, img in zip(SortOrder, sorter_imgs):
            self.vse.add_radiobutton(
                label=sorter.value,
                variable=sort_order,
                command=lambda: root.event_generate("<<SortExports>>"),
                image=img,
                compound="left",
            )
        self.vt.add_cascade(
            menu=self.vse,
            label="Sort Exports By",
            image=self.__sort_png,
            compound="left",
        )

        # Tools
        self.mt = mt = _Menu()
        self.add_cascade(menu=mt, label="Tools", underline=0)

        # Tools -> Demangler
        mt.add_command(label="Demangler", command=lambda *_: DemanglerWindow(root))

        # Help
        self.mh = mh = _Menu()
        self.add_cascade(menu=mh, label="Help", underline=0)

        # Help -> About
        self.__info_png = get_img("info.png")
        mh.add_command(
            accelerator="F1",
            command=lambda *_: self.open_about(),
            compound="left",
            image=self.__info_png,
            label="About",
        )
        self.bind_all("<F1>", lambda *_: self.open_about())

    def change_lang(self):
        """Instructs Tk to change the underlying locale.

        Generates:
            <<LanguageChanged>>: The UI is reinitialised by `dycall.app.App`.
        """
        lc = self.__locale
        lc.set(Lang2LCID[self.__lang.get()])
        MsgCat.locale(lc.get())
            self.__root.event_generate("<<LanguageChanged>>")
        log.info("Changed locale to '%s'", MsgCat.locale())

    # TODO: #1 Something is wrong in this or elsewhere.
    def update_recents(self, redraw: bool = False):
        """Clears (optionally) and repopulates **File** -> **Open Recents**.

        Args:
            redraw (bool, optional): Whether to clear the existing list of
                recents. Defaults to False.
        """
        if redraw:
            self.fop.delete(0, 9)
        for path in self.__recents:
            # pylint: disable=cell-var-from-loop
            self.fop.add_command(
                label=path, command=lambda *_: self.__root.picker.load(path=path)
            )

    def open_about(self):
        """Opens the **About** window in a singleton pattern."""
        if not self.__about_opened.get():
            self.__about_opened.set(True)
            AboutWindow(self.__root, self.__about_opened)
