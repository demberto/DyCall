# -*- coding: utf-8 -*-
from __future__ import annotations

import collections
import ctypes.util
import logging
import pathlib
import platform
from tkinter import filedialog

import lief
import ttkbootstrap as tk
from ttkbootstrap import ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.localization import MessageCatalog as MsgCat

from dycall.types import ELFExport, Export, PEExport

log = logging.getLogger(__name__)


class PickerFrame(ttk.Labelframe):
    def __init__(
        self,
        parent: tk.Window,
        lib_path: tk.StringVar,
        selected_export: tk.StringVar,
        output: tk.StringVar,
        status: tk.StringVar,
        is_loaded: tk.BooleanVar,
        is_native: tk.BooleanVar,
        default_title: str,
        exports: list[Export],
        recents: collections.deque,
    ):
        log.debug("Initialising")

        super().__init__(text="Library")
        self.__parent = parent
        self.__lib_path = lib_path
        self.__selected_export = selected_export
        self.__output = output
        self.__status = status
        self.__default_title = default_title
        self.__is_loaded = is_loaded
        self.__is_native = is_native
        self.__exports = exports
        self.__recents = recents
        self.os_name = platform.system()

        # Library path entry
        self.le = le = ttk.Entry(
            self,
            textvariable=self.__lib_path,
            validate="focusout",
            validatecommand=(self.register(self.validate), "%P"),
        )
        le.bind("<Return>", self.on_enter)
        le.pack(fill="x", expand=True, side="left", padx=5, pady=5)

        # Button to invoke file picker
        self.fb = fb = ttk.Button(
            self, text=MsgCat.translate("Browse"), command=self.browse
        )
        fb.pack(side="right", padx=(0, 5), pady=5)

        if lib_path.get():
            self.load()

        log.debug("Initialised")

    def on_enter(self, *_) -> None:
        # Without this, a false Export not found occurs
        self.__selected_export.set("")
        self.load()
        self.le.icursor("end")

    def validate(self, s: str) -> bool:
        if s:
            ret = ctypes.util.find_library(s)
            if ret:
                if ret == self.__lib_path.get():
                    # Enable
                    self.__parent.event_generate("<<ToggleExportsFrame>>", state=1)
                else:
                    self.load(path=ret)
            else:
                # Disable
                self.__parent.event_generate("<<ToggleExportsFrame>>", state=0)
                self.__parent.event_generate("<<ToggleFunctionFrame>>", state=0)
            return bool(ret)
        return True

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
            self.__selected_export.set("")
            self.load(True, file)

    def load(self, dont_search: bool = False, path: str = None) -> None:
        def failure():
            self.__is_loaded.set(False)
            self.__status.set("Load failed")
            Messagebox.show_error(f"Failed to load binary {path}", "Load failed")

        # Find absolute path
        if path is not None:
            self.__lib_path.set(path)
        else:
            path = self.__lib_path.get()
        if not dont_search:
            abspath = ctypes.util.find_library(path)
            if abspath is not None:
                path = abspath
                self.__lib_path.set(path)
        self.__output.set("")

        # * LIEF doesn't raise exceptions
        lib = lief.parse(path)
        if not isinstance(lib, lief.Binary):
            failure()
            return
        self.__parent.lib = lib
        self.__is_loaded.set(True)
        self.__status.set("Loaded successfully")
        lib_name = str(pathlib.Path(path).name)
        self.__parent.title(f"{self.__default_title} - {lib_name}")

        os = self.os_name
        fmt = lib.format
        fmts = lief.EXE_FORMATS

        if (
            (os == "Windows" and fmt == fmts.PE)
            or (os == "Darwin" and fmt == fmts.MACHO)
            or (os == "Linux" and fmt == fmts.ELF)
        ):
            self.__is_native.set(True)
        else:
            Messagebox.show_warning(
                f"{path} is not a native binary. You can view "
                "the exported functions but cannot call them.",
                "Not a native binary",
            )
            self.__is_native.set(False)

        self.__exports.clear()
        if fmt == fmts.PE:
            for exp in lib.get_export().entries:
                self.__exports.append(PEExport(exp.address, exp.name, exp.ordinal))
        elif fmt == fmts.ELF:
            for exp in lib.exported_symbols:
                self.__exports.append(
                    ELFExport(exp.value, exp.name, exp.demangled_name)
                )
        self.__parent.event_generate("<<PopulateExports>>")

        # Update recents
        if path not in self.__recents:
            self.__recents.append(path)
        else:
            self.__recents.remove(path)
            self.__recents.appendleft(path)
        self.__parent.event_generate("<<UpdateRecents>>")
