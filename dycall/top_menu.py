# -*- coding: utf-8 -*-
import collections
import logging
import platform

import ttkbootstrap as tk
from ttkbootstrap.localization import MessageCatalog as MsgCat

from dycall.about import AboutWindow
from dycall.demangler import DemanglerWindow
from dycall.types import SortOrder
from dycall.util import Lang2LCID, LCID2Lang, get_png

log = logging.getLogger(__name__)


class TopMenu(tk.Menu):
    # pylint: disable-next=too-many-locals
    def __init__(
        self,
        parent: tk.Window,
        outmode: tk.BooleanVar,
        locale: tk.StringVar,
        sort_order: tk.StringVar,
        show_get_last_error: tk.BooleanVar,
        show_errno: tk.BooleanVar,
        recents: collections.deque,
    ):
        super().__init__()
        self.__parent = parent
        self.__locale = locale
        self.__recents = recents
        self.__lang = tk.StringVar(value=LCID2Lang[locale.get()])

        # File
        self.fo = fo = tk.Menu()
        self.add_cascade(menu=fo, label="File", underline=0)

        # File -> Open Recent
        self.fop = fop = tk.Menu()
        self.__clock_png = get_png("clock.png")
        fo.add_cascade(
            menu=fop,
            label="Open Recent",
            underline=5,
            image=self.__clock_png,
            compound="left",
        )
        self.bind_all("<<UpdateRecents>>", lambda *_: self.update_recents(True))
        self.update_recents()

        # Options
        self.mo = mo = tk.Menu()
        self.add_cascade(menu=mo, label=MsgCat.translate("Options"), underline=0)

        # Options -> Language
        self.mol = mol = tk.Menu(mo)
        self.__translate_png = get_png("translate.png")
        for lang in LCID2Lang.values():
            mol.add_radiobutton(
                label=lang,
                variable=self.__lang,
                command=lambda: self.change_lang(),
            )
        mo.add_cascade(
            menu=mol,
            label=MsgCat.translate("Language"),
            image=self.__translate_png,
            compound="left",
        )

        # Options -> Theme
        self.mot = mot = tk.Menu(mo)
        self.__theme_png = get_png("theme.png")
        for label in ("System", "Light", "Dark"):
            mot.add_radiobutton(
                label=label, variable=parent.cur_theme, command=parent.set_theme
            )
        mo.add_cascade(
            menu=mot,
            label=MsgCat.translate("Theme"),
            image=self.__theme_png,
            compound="left",
        )

        # Options -> OUT mode
        mo.add_checkbutton(label=MsgCat.translate("OUT Mode"), variable=outmode)

        # Options -> Show GetLastError
        if platform.system() == "Windows":
            mo.add_checkbutton(
                label=MsgCat.translate("Show GetLastError"),
                variable=show_get_last_error,
                command=lambda: parent.event_generate(
                    "<<ToggleGetLastError>>", state=int(show_get_last_error.get())
                ),
            )

        # Options -> Show errno
        mo.add_checkbutton(
            label=MsgCat.translate("Show errno"),
            variable=show_errno,
            command=lambda: parent.event_generate(
                "<<ToggleErrno>>", state=int(show_errno.get())
            ),
        )

        # View
        self.vt = vt = tk.Menu()
        self.add_cascade(menu=vt, label=MsgCat.translate("View"), underline=0)

        # View -> Sort Exports By
        self.vse = vse = tk.Menu()
        self.__sort_png = get_png("sort.png")
        self.__sort_name_asc_png = get_png("sort_name_asc.png")
        self.__sort_name_desc_png = get_png("sort_name_desc.png")
        sorter_imgs = (
            self.__sort_name_asc_png,
            self.__sort_name_desc_png,
        )
        for sorter, img in zip(SortOrder, sorter_imgs):
            vse.add_radiobutton(
                label=MsgCat.translate(sorter.value),
                variable=sort_order,
                command=lambda: parent.event_generate("<<SortExports>>"),
                image=img,
                compound="left",
            )
        vt.add_cascade(
            menu=vse,
            label=MsgCat.translate("Sort Exports By"),
            image=self.__sort_png,
            compound="left",
        )

        # Tools
        self.mt = mt = tk.Menu()
        self.add_cascade(menu=mt, label=MsgCat.translate("Tools"), underline=0)

        # Tools -> Demangler
        mt.add_command(label="Demangler", command=lambda *_: DemanglerWindow(parent))

        # Help
        self.mh = mh = tk.Menu()
        self.add_cascade(menu=mh, label=MsgCat.translate("Help"), underline=0)

        # Help -> About
        self.__info_png = get_png("info.png")
        mh.add_command(
            accelerator="F1",
            command=lambda *_: self.open_about(),
            compound="left",
            image=self.__info_png,
            label=MsgCat.translate("About"),
        )
        self.bind_all("<F1>", lambda *_: self.open_about())

    def change_lang(self):
        log.debug("Changing language")
        lc = self.__locale
        lc.set(Lang2LCID[self.__lang.get()])
        MsgCat.locale(lc.get())
        self.__parent.event_generate("<<LanguageChanged>>")
        log.info("Changed locale to '%s'", MsgCat.locale())

    def update_recents(self, redraw=False):
        if redraw:
            self.fop.delete(0, 9)
        for path in self.__recents:
            # pylint: disable=cell-var-from-loop
            self.fop.add_command(
                label=path, command=lambda *_: self.__parent.picker.load(path=path)
            )

    def open_about(self):
        AboutWindow(self.__parent)
