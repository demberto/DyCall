import logging

import ttkbootstrap as tk
from ttkbootstrap import ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.localization import MessageCatalog as MC

from dycall.util import DemangleError, PlatformUnsupportedError, demangle

log = logging.getLogger(__name__)


class ExportsFrame(ttk.Labelframe):
    def __init__(
        self,
        parent: tk.Window,
        export: tk.StringVar,
        output: tk.StringVar,
        status: tk.StringVar,
        is_native: tk.BooleanVar,
    ):
        log.debug("Initalising")

        super().__init__(text=MC.translate("Exports"))
        self.__parent = parent
        self.__selected_export = export
        self.__output = output
        self.__status = status
        self.__is_native = is_native

        self.cb = cb = ttk.Combobox(self, state="disabled", textvariable=export)
        cb.bind("<<ComboboxSelected>>", self.cb_selected)
        cb.pack(fill="x", padx=5, pady=5)

        log.debug("Initialised")

    def cb_selected(self, *_):
        log.debug("{} selected", self.__selected_export.get())
        self.__output.set("")
        func_frame = self.__parent.function
        if self.__is_native.get():
            func_frame.set_state()
        else:
            func_frame.set_state(False)

    def set_state(self, activate=True):
        log.debug("Called with activate={}", activate)
        state = "readonly" if activate else "disabled"
        self.cb.configure(state=state)

    def set_cb_values(self, exports):
        num_exports = len(exports)
        log.info("Found {} exports", num_exports)
        self.set_state()
        demangled = []
        failed = []
        for exp in exports:
            try:
                log.debug("Demangling {}", exp)
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
        export_names = demangled + failed
        self.cb.configure(values=export_names)
        selected_export = self.__selected_export.get()
        if selected_export:
            if selected_export not in export_names:
                err = f"{selected_export} not found in export names"
                log.error(err)
                Messagebox.show_error(err, "Export not found", parent=self.__parent)
                self.cb.set("")
            else:
                # Activate function frame when export name is passed from command line
                self.cb_selected()
        self.__status.set(f"{num_exports} exports found")
        if failed:
            Messagebox.show_warning(
                f"These export names couldn't be demangled: {failed}",
                "Demangle Failed",
                parent=self.__parent,
            )
