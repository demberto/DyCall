#!/usr/bin/env python3

"""
dycall.exports
~~~~~~~~~~~~~~

Contains `ExportsFrame` and `ExportsTreeView`.
"""

from __future__ import annotations

import logging
import pathlib
from typing import TYPE_CHECKING

import ttkbootstrap as tk
from ttkbootstrap import ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.localization import MessageCatalog as MsgCat
from ttkbootstrap.tableview import Tableview

from dycall.types import Export, PEExport
from dycall.util import StaticThemedTooltip, get_img

log = logging.getLogger(__name__)


class ExportsFrame(ttk.Labelframe):
    """Contains **Exports** combobox and a button for `ExportsTreeView`.

    Use command line argument `--exp` to select an export from the library on
    launch. Combobox validates export name.

    TODO: Combobox works like google search (auto-suggest, recents etc.)
    """

    def __init__(
        self,
        root: tk.Window,
        selected_export: tk.StringVar,
        sort_order: tk.StringVar,
        output: tk.StringVar,
        status: tk.StringVar,
        is_loaded: tk.BooleanVar,
        is_native: tk.BooleanVar,
        is_reinitialised: tk.BooleanVar,
        lib_path: tk.StringVar,
        exports: list[Export],
    ):
        log.debug("Initalising")

        super().__init__(text=MsgCat.translate("Exports"))
        self.__root = root
        self.__selected_export = selected_export
        self.__sort_order = sort_order
        self.__output = output
        self.__status = status
        self.__is_loaded = is_loaded
        self.__is_native = is_native
        self.__is_reinitialised = is_reinitialised
        self.__lib_path = lib_path
        self.__exports = exports
        self.__export_names: list[str] = []

        self.cb = cb = ttk.Combobox(
            self,
            state="disabled",
            textvariable=selected_export,
            validate="focusout",
            validatecommand=(self.register(self.cb_validate), "%P"),
        )
        # ! cb.bind("<Return>", lambda *_: self.cb_validate)  # Doesn't work
        cb.bind("<<ComboboxSelected>>", self.cb_selected)

        self.__list_png = get_img("list.png")
        self.lb = lb = ttk.Label(self, image=self.__list_png)
        lb.bind(
            "<Enter>",
            lambda *_: StaticThemedTooltip(lb, MsgCat.translate("List of exports")),
        )
        lb.bind("<ButtonRelease-1>", lambda *_: status.set("Load a library first!"))

        lb.pack(padx=(0, 5), pady=5, side="right")
        cb.pack(fill="x", padx=5, pady=5)

        self.bind_all("<<PopulateExports>>", lambda *_: self.set_cb_values())
        self.bind_all(
            "<<ToggleExportsFrame>>", lambda event: self.set_state(event.state == 1)
        )
        self.bind_all("<<SortExports>>", lambda *_: self.sort())
        log.debug("Initialised")

    def cb_selected(self, *_):
        """Callback to handle clicks on **Exports** combobox.

        Resets **Output** and activates/deactivates `FunctionFrame`.
        """
        log.debug("%s selected", self.__selected_export.get())
        self.__output.set("")
        if self.__is_native.get():
            self.__root.event_generate("<<ToggleFunctionFrame>>", state=1)
        else:
            self.__root.event_generate("<<ToggleFunctionFrame>>", state=0)

    def cb_validate(self, *_) -> bool:
        """Callback to handle keyboard events on **Exports** combobox.

        Activates `FunctionFrame` when the text in the combobox
        is a valid export name. Deactivates it otherwise.
        """
        log.debug("Validating Exports combobox")
        try:
            # Don't validate if combobox dropdown arrow was pressed
            self.cb.state()[1] == "pressed"
        except IndexError:
            exp = self.cb.get()
            if exp:
                if exp in self.__export_names:
                    self.cb_selected()
                    return True
                self.__root.event_generate("<<ToggleFunctionFrame>>", state=1)
                return False
        return True

    def set_state(self, activate: bool = True):
        """Activates/deactivates **Exports** combobox.

        Args:
            activate (bool, optional): Activated when True, deactivated when
                False. Defaults to True.
        """
        log.debug("Called with activate=%s", activate)
        state = "normal" if activate else "disabled"
        self.cb.configure(state=state)

    def set_cb_values(self):
        """Demangles and sets the export names to the **Exports** combobox."""
        exports = self.__exports
        if not self.__is_reinitialised.get() or self.__is_loaded.get():
            num_exports = len(exports)
            log.info("Found %d exports", num_exports)
            self.__status.set(f"{num_exports} exports found")
            failed = []
            for exp in exports:
                if isinstance(exp, PEExport):
                    if hasattr(exp, "exc"):
                        failed.append(exp.name)
            if failed:
                Messagebox.show_warning(
                    f"These export names couldn't be demangled: {failed}",
                    "Demangle Errors",
                    parent=self.__root,
                )
        self.__export_names = names = list(e.demangled_name for e in exports)
        self.set_state()
        self.cb.configure(values=names)
        selected_export = self.__selected_export.get()
        if selected_export:
            if selected_export not in names:
                err = "%s not found in export names"
                log.error(err, selected_export)
                Messagebox.show_error(
                    err % selected_export, "Export not found", parent=self.__root
                )
                self.cb.set("")
            else:
                # Activate function frame when export name is passed from command line
                self.cb_selected()
        self.lb.configure(cursor="hand2")
        self.lb.bind(
            "<ButtonRelease-1>",
            lambda *_: ExportsTreeView(
                self.__exports, pathlib.Path(self.__lib_path.get()).name
            ),
            add=False,
        )

    def sort(self, *_):
        """Sorts the list of export names and repopulates the combobox."""
        if self.__is_loaded.get():
            sorter = self.__sort_order.get()
            log.debug("Sorting w.r.t. %s", sorter)
            names = self.__export_names
            if sorter == "Name (ascending)":
                names.sort()
            elif sorter == "Name (descending)":
                names.sort(reverse=True)
            self.cb.configure(values=names)
        self.__status.set("Sort order changed")


class ExportsTreeView(tk.Toplevel):
    """Displays detailed information about all the exports of a library.

    Following information is displayed:
    - Address
    - Name
    - Demangled name (whenever available)
    - Ordinal (Windows only)
    """

    def __init__(self, exports: list[Export], lib_name: str):
        log.debug("Initialising")
        super().__init__(
            title=f"{MsgCat.translate('Exports')} - {lib_name}", size=(400, 500)
        )
        self.__old_height = 0
        self.withdraw()
        coldata = [
            "Address",
            "Name",
            {"text": "Demangled", "stretch": True},
        ]
        is_pe = isinstance(exports[0], PEExport)
        if is_pe:
            coldata.insert(0, "Ordinal")
        self.__tv = tv = Tableview(
            self,
            searchable=True,
            autofit=True,
            coldata=coldata,
            paginated=True,
            pagesize=25,
        )
        tv.pack(fill="both", expand=True)
        for e in exports:
            values = [e.address, e.name, e.demangled_name]  # type: ignore
            if is_pe:
                if TYPE_CHECKING:
                    assert isinstance(e, PEExport)  # nosec
                values.insert(0, e.ordinal)
            tv.insert_row(values=values)
        tv.load_table_data()
        self.bind(
            "<F11>",
            lambda *_: self.attributes(
                "-fullscreen", not self.attributes("-fullscreen")
            ),
        )
        self.bind("<Configure>", self.resize)
        self.deiconify()
        self.focus_set()
        log.debug("Initialised")

    def resize(self, event: tk.tk.Event):
        """Change the treeview's `pagesize` whenever this window is resized.

        I came up with this because there is no way to show a vertical
        scrollbar in/for the treeview.
        """
        new_height = event.height
        if event.widget.widgetName == "toplevel" and new_height != self.__old_height:
            # ! This is an expensive call, avoid it whenever possible
            self.__tv.pagesize = int(new_height) / 20
            self.__old_height = new_height
