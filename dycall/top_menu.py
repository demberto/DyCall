# -*- coding: utf-8 -*-
import logging

import ttkbootstrap as tk
from ttkbootstrap.localization import MessageCatalog as MC

from dycall.about import AboutWindow
from dycall.demangler import DemanglerWindow
from dycall.util import Lang2LCID, LCID2Lang

log = logging.getLogger(__name__)


class TopMenu(tk.Menu):
    def __init__(self, parent, outmode: tk.BooleanVar, locale: tk.StringVar):
        super().__init__()
        self.parent = parent
        self.locale_var = locale
        self.lang_var = tk.StringVar(value=LCID2Lang[locale.get()])

        # Options
        self.mo = mo = tk.Menu()
        self.add_cascade(menu=mo, label=MC.translate("Options"))

        # Options -> Language
        self.mol = mol = tk.Menu(mo)
        for lang in LCID2Lang.values():
            mol.add_radiobutton(
                label=lang,
                variable=self.lang_var,
                command=self.change_lang,
            )
        mo.add_cascade(menu=mol, label=MC.translate("Language"))

        # Options -> Theme
        self.mot = mot = tk.Menu(mo)
        for label in ("System", "Light", "Dark"):
            mot.add_radiobutton(
                label=label, variable=parent.cur_theme, command=parent.set_theme
            )
        mo.add_cascade(menu=mot, label=MC.translate("Theme"))

        # Options -> OUT mode
        mo.add_checkbutton(label="OUT Mode", variable=outmode)

        # Tools
        self.mt = mt = tk.Menu()
        self.add_cascade(menu=mt, label=MC.translate("Tools"))

        # Tools -> Demangler
        mt.add_command(label="Demangler", command=lambda *_: DemanglerWindow(parent))

        # Help
        self.mh = mh = tk.Menu()
        self.add_cascade(menu=mh, label=MC.translate("Help"))

        # Help -> About
        mh.add_command(
            label=MC.translate("About"), command=lambda *_: AboutWindow(parent)
        )

    def change_lang(self, *_):
        lc = self.locale_var
        lc.set(Lang2LCID[self.lang_var.get()])
        MC.locale(lc.get())
        self.parent.refresh()
        log.info("Changed locale to '%s'", MC.locale())
