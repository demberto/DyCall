# -*- coding: utf-8 -*-
import logging

import ttkbootstrap as tk
from ttkbootstrap.localization import MessageCatalog as MsgCat

from dycall.about import AboutWindow
from dycall.demangler import DemanglerWindow
from dycall.types import SortOrder
from dycall.util import Lang2LCID, LCID2Lang

log = logging.getLogger(__name__)


class TopMenu(tk.Menu):
    def __init__(
        self,
        parent,
        outmode: tk.BooleanVar,
        locale: tk.StringVar,
        sort_order: tk.StringVar,
    ):
        super().__init__()
        self.parent = parent
        self.__locale = locale
        self.__lang = tk.StringVar(value=LCID2Lang[locale.get()])

        # Options
        self.mo = mo = tk.Menu()
        self.add_cascade(menu=mo, label=MsgCat.translate("Options"))

        # Options -> Language
        self.mol = mol = tk.Menu(mo)
        for lang in LCID2Lang.values():
            mol.add_radiobutton(
                label=lang,
                variable=self.__lang,
                command=self.change_lang,
            )
        mo.add_cascade(menu=mol, label=MsgCat.translate("Language"))

        # Options -> Theme
        self.mot = mot = tk.Menu(mo)
        for label in ("System", "Light", "Dark"):
            mot.add_radiobutton(
                label=label, variable=parent.cur_theme, command=parent.set_theme
            )
        mo.add_cascade(menu=mot, label=MsgCat.translate("Theme"))

        # Options -> OUT mode
        mo.add_checkbutton(label="OUT Mode", variable=outmode)

        # View
        self.vt = vt = tk.Menu()
        self.add_cascade(menu=vt, label=MsgCat.translate("View"))

        # View -> Sort Exports By
        self.vse = vse = tk.Menu()
        for sorter in SortOrder:
            vse.add_radiobutton(
                label=MsgCat.translate(sorter.value),
                variable=sort_order,
                command=parent.exports.sort,
            )
        vt.add_cascade(menu=vse, label=MsgCat.translate("Sort Exports By"))

        # Tools
        self.mt = mt = tk.Menu()
        self.add_cascade(menu=mt, label=MsgCat.translate("Tools"))

        # Tools -> Demangler
        mt.add_command(label="Demangler", command=lambda *_: DemanglerWindow(parent))

        # Help
        self.mh = mh = tk.Menu()
        self.add_cascade(menu=mh, label=MsgCat.translate("Help"))

        # Help -> About
        mh.add_command(
            label=MsgCat.translate("About"), command=lambda *_: AboutWindow(parent)
        )

    def change_lang(self, *_):
        lc = self.__locale
        lc.set(Lang2LCID[self.__lang.get()])
        MsgCat.locale(lc.get())
        self.parent.refresh()
        log.info("Changed locale to '%s'", MsgCat.locale())
