# pylint: disable=too-many-locals

from __future__ import annotations

import logging
import queue
from typing import NamedTuple

import tksheet
import ttkbootstrap as tk
from ttkbootstrap import ttk
from ttkbootstrap.localization import MessageCatalog as MC

from dycall.runner import Runner
from dycall.types import CALL_CONVENTIONS, PARAMETER_TYPES, Marshaller

log = logging.getLogger(__name__)


class FunctionFrame(ttk.Frame):
    def __init__(
        self,
        parent: tk.Window,
        call_conv: tk.StringVar,
        returns: tk.StringVar,
        lib_path: tk.StringVar,
        export: tk.StringVar,
        output: tk.StringVar,
        status: tk.StringVar,
        is_outmode: tk.BooleanVar,
        is_running: tk.BooleanVar,
        rows_to_add: int,
    ):
        super().__init__()
        self.__parent = parent
        self.__call_conv = call_conv
        self.__returns = returns
        self.__lib_path = lib_path
        self.__export = export
        self.__output = output
        self.__status = status
        self.__is_outmode = is_outmode
        self.__is_running = is_running
        self.__que = queue.Queue()
        self.__exc = queue.Queue()
        self.__args = []

        # Call convention
        cg = ttk.Labelframe(self, text="Calling Convention")
        self.cc = cc = ttk.Combobox(
            cg,
            values=CALL_CONVENTIONS,
            textvariable=call_conv,
            state="disabled",
            font=("Courier", 9),
        )
        if not call_conv.get():
            cc.current(0)  # CallConvention.cdecl

        # Return type
        rg = ttk.Labelframe(self, text="Returns")
        self.rc = rc = ttk.Combobox(
            rg,
            values=PARAMETER_TYPES,
            textvariable=returns,
            state="disabled",
            font=("Courier", 9),
        )
        if not returns.get():
            rc.current(7)  # ParameterType.i (int32_t)

        # Run
        self.rb = rb = ttk.Button(
            self,
            text=f"{MC.translate('Run')}\n(F5)",
            state="disabled",
            command=self.run,
        )

        # Arguments table
        self.ag = ag = ttk.Labelframe(self, text="Arguments")
        self.at = at = tksheet.Sheet(
            ag,
            headers=[MC.translate("Type"), MC.translate("Value")],
            empty_horizontal=20,
            row_height=25,
            data=self.__args,
            paste_insert_column_limit=True,
            show_top_left=False,
        )
        at.extra_bindings("end_edit_cell", self.table_end_edit_cell)
        at.extra_bindings("end_insert_rows", self.table_end_insert_rows)
        at.extra_bindings("end_paste", self.table_end_paste)
        at.readonly_columns(columns=[0])
        at.default_row_height(height=30)
        at.column_width(1, width=250)
        if rows_to_add > 0:
            for row_index in range(rows_to_add):
                at.insert_row()
                self.table_end_insert_rows(row=row_index)

        cc.grid(sticky="ew", padx=5, pady=5)
        rc.grid(sticky="ew", padx=5, pady=5)
        at.grid(sticky="nsew", padx=5, pady=5)

        cg.grid(row=0, column=0, sticky="ew", padx=5)
        rg.grid(row=0, column=1, sticky="ew")
        rb.grid(row=0, column=2, padx=5)
        ag.grid(row=1, columnspan=3, sticky="nsew", padx=5, pady=5)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        cg.columnconfigure(0, weight=1)
        rg.columnconfigure(0, weight=1)
        ag.rowconfigure(0, weight=1)
        ag.columnconfigure(0, weight=1)

    def table_end_insert_rows(self, event: NamedTuple = None, row: int = None):
        if event is not None:
            param1 = event[1]
        else:
            param1 = row
        self.at.create_dropdown(
            r=param1,
            c=0,
            set_value="uint32_t",
            values=PARAMETER_TYPES,
            redraw=True,
            selection_function=self.table_dropdown_change,
        )
        self.at.set_cell_data(r=param1, c=1, value="0")

    def table_end_edit_cell(self, event: NamedTuple):
        row, col, _, text, *_ = event
        if col == 1:
            self.table_validate(row, text)
        else:
            self.at.dehighlight_cells(row, 1)

    def table_end_paste(self, event: NamedTuple):
        _, (x, y), content = event
        if isinstance(x, int):
            row, col = x, y
            if col == 1:
                text = content[0][0]
                self.table_validate(row, text)
        # TODO
        # elif isinstance(x, str):
        #    what, which = x, y

    def table_validate(self, row: int, text: str):
        t = self.at.get_cell_data(row, 0)
        try:
            if t == "bool":
                assert text in ("True", "False")
            elif t in ("float", "double"):
                float(text)
            elif t not in ("char", "char*", "wchar_t", "wchar_t*"):
                int(text)
        # https://stackoverflow.com/a/6470452
        except (AssertionError, ValueError):
            self.at.highlight_cells(row, 1, bg="red")
        else:
            self.at.dehighlight_cells(row, 1)

    def set_state(self, activate: bool = True):
        if activate:
            self.rc.configure(state="readonly")
            self.cc.configure(state="readonly")
            self.rb.configure(state="normal")
            self.at.enable_bindings()
            for binding in ("rc_insert_column", "rc_delete_column", "cut", "delete"):
                self.at.disable_bindings(binding)
            self.bind_run_button()
        else:
            for w in (self.rc, self.cc, self.rb):
                w.configure(state="disabled")
            self.at.disable_bindings()
            self.unbind_run_button()

    def table_dropdown_change(self, event):
        # pylint: disable=no-else-return
        # pylint: disable=bare-except

        row, _, _, type_ = event
        t = self.at

        if type_ == "bool":
            t.create_dropdown(row, 1, values=["True", "False"], redraw=True)
            return
        else:
            try:
                t.delete_dropdown(row, 1)
            except:
                t.set_cell_data(row, 1)

        if type_ == "void":
            t.set_cell_data(row, 1, value="NULL")
            t.readonly_cells(row, 1, readonly=True)
            return
        else:
            t.readonly_cells(row, 1, readonly=False)

        if type_ in ("float", "double"):
            t.set_cell_data(row, 1, value="0.0")
        elif type_ not in ("char", "char*", "void*", "wchar_t", "wchar_t*"):
            t.set_cell_data(row, 1, value="0")

    def process_queue(self):
        try:
            exc = self.__exc.get_nowait()
        except queue.Empty:
            pass
        else:
            log.exception(exc)
            raise exc

        try:
            result = self.__que.get_nowait()
        except queue.Empty:
            self.after(100, self.process_queue)
        else:
            output_frame = self.__parent.output
            output_frame.configure(text="Output")
            self.__status.set("Operation successful")
            ret = Marshaller.pytype2str(result.ret)
            self.__output.set(ret)
            if self.__is_outmode.get():
                self.at.set_column_data(1, result.values, redraw=True)
            self.activate_copy_button()
            self.rb.configure(state="normal")

    def run(self, *_):
        def handle_exc(e: Exception, status: str):
            log.exception(e)
            etype = type(e).__name__
            self.__parent.output.configure(text=etype)
            self.__output.set(str(e))
            self.__status.set(status)
            self.activate_copy_button(bootstyle="danger")
            self.rb.configure(state="normal")
            self.bind_run_button()

        ret_type = self.__returns.get()
        self.__status.set("Running...")
        self.rb.configure(state="disabled")
        self.unbind_run_button()

        try:
            thread = Runner(
                self.__exc,
                self.__que,
                self.__args,
                self.__call_conv.get(),
                ret_type,
                self.__lib_path.get(),
                self.__export.get(),
            )
        except Exception as e:  # pylint: disable=broad-except
            handle_exc(e, "Invalid argument(s)")
            return
        self.__is_running.set(True)
        thread.start()

        try:
            self.process_queue()
        except Exception as e:  # pylint: disable=broad-except
            handle_exc(e, "An error occured")
        self.__is_running.set(False)

    # * Helpers
    def activate_copy_button(self, state="normal", bootstyle="default"):
        self.__parent.output.oc.configure(state=state, bootstyle=bootstyle)

    def bind_run_button(self):
        # pylint: disable=attribute-defined-outside-init
        self.__run_binding = self.bind_all("<F5>", self.run)

    def unbind_run_button(self):
        self.unbind("<F5>", self.__run_binding)
