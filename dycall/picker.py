#!/usr/bin/env python3

"""
dycall.picker
~~~~~~~~~~~~~

Contain `PickerFrame`.
"""

from __future__ import annotations

import collections
import ctypes.util
import logging
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
    """Implements the library picker.

    Use command line option `--lib` to auto-load a library on app launch.

    Features:
    - Validation
    - Supports short names (thanks to system search order)
    - Remembers recently opened files.
    """

    def __init__(
        self,
        root: tk.Window,
        lib_path: tk.StringVar,
        selected_export: tk.StringVar,
        output: tk.StringVar,
        status: tk.StringVar,
        is_loaded: tk.BooleanVar,
        is_native: tk.BooleanVar,
        exports: list[Export],
        recents: collections.deque,
    ):
        log.debug("Initialising")

        super().__init__(text="Library")
        self.__root = root
        self.__lib_path = lib_path
        self.__selected_export = selected_export
        self.__output = output
        self.__status = status
        self.__is_loaded = is_loaded
        self.__is_native = is_native
        self.__exports = exports
        self.__recents = recents
        self.__os_name = platform.system()

        # Library path entry
        self.le = le = ttk.Entry(
            self,
            textvariable=self.__lib_path,
            validate="focusout",
            validatecommand=(self.register(self.validate), "%P"),
        )
        le.bind("<Return>", self.on_return_key)
        le.pack(fill="x", expand=True, side="left", padx=5, pady=5)

        # Button to invoke file picker
        self.fb = fb = ttk.Button(
            self, text=MsgCat.translate("Browse"), command=self.browse
        )
        fb.pack(side="right", padx=(0, 5), pady=5)

        if lib_path.get():
            self.load()

        log.debug("Initialised")

    def on_return_key(self, *_) -> None:
        """Callback for handling Enter key pressed in **Library** entry."""
        # Without this, a false Export not found occurs
        self.__selected_export.set("")
        self.load()
        self.le.icursor("end")

    def validate(self, s: str) -> bool:
        """Picker entry validation logic.

        Toggles the state of **Exports** and **Function** frame depending upon
        the result of the validation.
        """
        if s:
            ret = ctypes.util.find_library(s)
            if ret:
                if ret == self.__lib_path.get():
                    # Enable
                    self.__root.event_generate("<<ToggleExportsFrame>>", state=1)
                else:
                    self.load(path=ret)
            else:
                # Disable
                self.__root.event_generate("<<ToggleExportsFrame>>", state=0)
                self.__root.event_generate("<<ToggleFunctionFrame>>", state=0)
            return bool(ret)
        return True

    def browse(self) -> None:
        """Opens a file picker to select a library."""
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
        """Implements the library load logic.

        1. Finds absolute path if `dont_search` is `False`.
        2. Parses the library with LIEF.
        3. Checks if it is a native library.
        4. Triggers the population of **Exports** combobox.
        5. Updates recents.

        Args:
            dont_search (bool, optional): Don't use the system search
                order for finding the library. Defaults to False.
            path (str, optional): Used instead of `self.__lib_path` as the library
                path. Defaults to None. If None, then `self.__lib_path` is used.
        """

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
        self.__is_loaded.set(True)
        self.__status.set("Loaded successfully")
        self.__root.event_generate("<<SetWindowTitle>>")

        os = self.__os_name
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
        self.__root.event_generate("<<PopulateExports>>")

        # Update recents
        if path not in self.__recents:
            self.__recents.append(path)
        else:
            self.__recents.remove(path)
            self.__recents.appendleft(path)
        self.__root.event_generate("<<UpdateRecents>>")
