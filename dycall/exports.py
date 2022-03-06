# -*- coding: utf-8 -*-
from __future__ import annotations

import logging

import ttkbootstrap as tk
from ttkbootstrap import ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.localization import MessageCatalog as MsgCat

from dycall.util import DemangleError, PlatformUnsupportedError, demangle

log = logging.getLogger(__name__)


class ExportsFrame(ttk.Labelframe):
    def __init__(
        self,
        parent: tk.Window,
        export: tk.StringVar,
        output: tk.StringVar,
        status: tk.StringVar,
        is_loaded: tk.BooleanVar,
        is_native: tk.BooleanVar,
        is_reinitialised: tk.BooleanVar,
        exports: list[str],
    ):
        log.debug("Initalising")

        super().__init__(text=MsgCat.translate("Exports"))
        self.__parent = parent
        self.__selected_export = export
        self.__output = output
        self.__status = status
        self.__is_loaded = is_loaded  # pylint: disable=unused-private-member # TODO
        self.__is_native = is_native
        self.__is_reinitialised = is_reinitialised
        self.__exports = exports

        self.cb = cb = ttk.Combobox(self, state="disabled", textvariable=export)
        cb.bind("<<ComboboxSelected>>", self.cb_selected)
        cb.pack(fill="x", padx=5, pady=5)

        log.debug("Initialised")

    def cb_selected(self, *_):
        """Callback to handle clicks on **Exports** combobox.

        Resets **Output** and activates/deactivates `FunctionFrame`.
        """
        log.debug("%s selected", self.__selected_export.get())
        self.__output.set("")
        func_frame = self.__parent.function
        if self.__is_native.get():
            func_frame.set_state()
        else:
            func_frame.set_state(False)

    def set_state(self, activate=True):
        """Activates/deactivates **Exports** combobox.

        Args:
            activate (bool, optional): Activated when True, deactivated when
                False. Defaults to True.
        """
        log.debug("Called with activate=%s", activate)
        state = "readonly" if activate else "disabled"
        self.cb.configure(state=state)

    def set_cb_values(self):
        """Demangles and sets the export names to the **Exports** combobox."""
        exports = self.__exports
        num_exports = len(exports)
        log.info("Found %d exports", num_exports)
        if not self.__is_reinitialised.get():
            demangled = []
            failed = []
            for exp in exports:
                try:
                    log.debug("Demangling %s", exp)
                    d = demangle(exp)
                except DemangleError as exc:
                    log.exception(exc)
                    failed.append(exp)
                except PlatformUnsupportedError as exc:
                    log.exception(exc)
                    failed = exports
                    break
                else:
                    demangled.append(d)
            self.__exports.clear()
            self.__exports.extend(demangled + failed)
            if failed:
                Messagebox.show_warning(
                    f"These export names couldn't be demangled: {failed}",
                    "Demangle Failed",
                    parent=self.__parent,
                )
        else:
            self.__exports.clear()
            self.__exports.extend(exports)
        self.set_state()
        self.cb.configure(values=self.__exports)
        selected_export = self.__selected_export.get()
        if selected_export:
            if selected_export not in self.__exports:
                err = "%s not found in export names"
                log.error(err, selected_export)
                Messagebox.show_error(
                    err % selected_export, "Export not found", parent=self.__parent
                )
                self.cb.set("")
            else:
                # Activate function frame when export name is passed from command line
                self.cb_selected()
        self.__status.set(f"{num_exports} exports found")
