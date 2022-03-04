from __future__ import annotations

import ctypes.util
import logging
import pathlib
import platform
from tkinter import filedialog

import lief
import ttkbootstrap as tk
from ttkbootstrap import ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.localization import MessageCatalog as MC

log = logging.getLogger(__name__)


class PickerFrame(ttk.Labelframe):
    def __init__(
        self,
        parent: tk.Window,
        lib_path: tk.StringVar,
        selected_export: tk.StringVar,
        output: tk.StringVar,
        status: tk.StringVar,
        is_native: tk.BooleanVar,
        default_title: str,
    ):
        log.debug("Initialising")

        super().__init__(text="Library")
        self.parent = parent
        self.lib_path = lib_path
        self.selected_export = selected_export
        self.output = output
        self.status = status
        self.is_native = is_native
        self.window_title = default_title
        self.os_name = platform.system()
        is_file = self.register(self.validate)

        # Library path entry
        self.le = le = ttk.Entry(
            self,
            textvariable=self.lib_path,
            validate="focusout",
            validatecommand=(is_file, "%P"),
        )
        le.bind("<Return>", self.on_enter)
        le.pack(fill="x", expand=True, side="left", padx=5, pady=5)

        # Button to invoke file picker
        self.fb = fb = ttk.Button(
            self, text=MC.translate("Browse"), command=self.browse
        )
        fb.pack(side="right", padx=(0, 5), pady=5)

        if lib_path.get():
            self.load()

        log.debug("Initialised")

    def on_enter(self, *_) -> None:
        # Without this, a false Export not found occurs
        self.selected_export.set("")
        self.load()
        self.le.icursor("end")

    def validate(self, s) -> bool:
        ret = pathlib.Path(s).is_file()
        exports_frame = self.parent.exports
        function_frame = self.parent.function
        if ret:
            if s == self.lib_path.get():
                exports_frame.set_state(True)
            else:
                # TODO Changing the library path directly doesn't invoke this
                # * Return needs to pressed for load to get called actually
                self.load(path=s)
        else:
            exports_frame.set_state(False)
            function_frame.set_state(False)
        return ret

    def browse(self) -> None:
        file = filedialog.askopenfilename(
            title="Select a binary to load",
            filetypes=[
                ("All files", "*.*"),
                ("PE DLL", "*.dll"),
                ("ELF shared object", "*.so"),
                ("MachO dynamic library", "*.dylib"),
            ],
        )
        if file:
            # Without this, a false Export not found occurs
            self.selected_export.set("")
            self.load(True, file)

    def load(self, dont_search=False, path=None) -> None:
        def failure():
            self.status.set("Load failed")
            Messagebox.show_error("Load failed", f"Failed to load binary {path}")

        if path:
            self.lib_path.set(path)
        else:
            path = self.lib_path.get()
        if not dont_search:
            abspath = ctypes.util.find_library(path)
            if abspath is not None:
                path = abspath
                self.lib_path.set(path)
        self.output.set("")

        # * LIEF doesn't raise exceptions, instead returns the exception object
        lib = lief.parse(path)
        if isinstance(lib, lief.lief_errors):
            failure()
            return
        self.parent.lib = lib
        self.status.set("Loaded successfully")

        lib_name = str(pathlib.Path(path).name)
        self.parent.title(f"{self.window_title} - {lib_name}")

        os = self.os_name
        fmt = lib.format
        fmts = lief.EXE_FORMATS

        # pylint: disable-next=too-many-boolean-expressions
        if (
            (os == "Windows" and fmt == fmts.PE)
            or (os == "Darwin" and fmt == fmts.MACHO)
            or (os == "Linux" and fmt == fmts.ELF)
        ):
            self.is_native.set(True)
        else:
            Messagebox.show_warning(
                "Not a native binary",
                f"{path} is not a native binary. You can view "
                "the exported functions but cannot call them.",
            )
            self.is_native.set(False)

        exports = tuple(e.name for e in lib.exported_functions)
        self.parent.exports.set_cb_values(exports)
