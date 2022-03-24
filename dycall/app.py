# -*- coding: utf-8 -*-
from __future__ import annotations

import collections
import logging
import os
import pathlib
import platform
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from typing import Final  # type: ignore
    except ImportError:
        from typing_extensions import Final  # type: ignore

# pylint: disable=wrong-import-position
import appdirs
import darkdetect
import easysettings
import ttkbootstrap as tk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.icons import Icon
from ttkbootstrap.localization import MessageCatalog as MsgCat

from dycall.exports import ExportsFrame
from dycall.function import FunctionFrame
from dycall.output import OutputFrame
from dycall.picker import PickerFrame
from dycall.status_bar import StatusBarFrame
from dycall.top_menu import TopMenu
from dycall.types import CallConvention, Export, SortOrder
from dycall.util import DARK_THEME, LIGHT_THEME, set_app_icon

log = logging.getLogger(__name__)

# https://stackoverflow.com/a/3430395
dirpath = pathlib.Path(__file__).parent.resolve()


class App(tk.Window):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        conv: str = CallConvention.Cdecl.value,
        exp: str = "",
        lib: str = "",
        ret: str = "",
        rows: int = 0,
        lang: str = "",
        out_mode: bool = False,
        hide_last_err: bool = False,
        hide_errno: bool = False,
    ) -> None:
        """DyCall entry point.

        Certain arguments can be passed from the command line directly. These
        arguments will be used to initalise the interface. This helps achieve
        some automation and it also saves my time while testing. The default
        arguments aren't the default values used by DyCall interface.

        Args:
            conv (str, optional): Calling convention. Defaults to "cdecl".
            exp (str, optional): Name of exported function. Defaults to "".
            lib (str, optional): Path/name of the library. Defaults to "".
            ret (str, optional): Return type. See `ParameterType`. Defaults to "".
            rows (int, optional): Number of empty rows to add to arguments table.
                Defaults to 0.
            lang (str, optional): The language used for displaying UI. Defaults to "".
            out_mode (bool, optional): Whether **OUT Mode** should be enabled.
                Defaults to False.
            hide_last_err (bool, optional): Hides and doesn't retrieve GetLastError
                value shown in status bar. (Windows only)
            hide_errno (bool, optional): Hides and doesn't retrieve errno value
                shown in status bar.
        """  # noqa: D403
        log.debug("Initialising")
        self.__rows_to_add: Final = rows
        self.__exports: list[Export] = []
        self.__recents: Final[collections.deque] = collections.deque(maxlen=10)

        # No need to save a preference in the config when
        # DyCall is passed with it from the command line.
        self.__dont_save_locale = False
        self.__dont_save_out_mode = False
        self.__dont_save_show_get_last_error = False
        self.__dont_save_show_errno = False

        super().__init__(iconphoto=None)
        self.withdraw()

        log.debug("Loading config")
        configdir = appdirs.user_config_dir("DyCall", "demberto")
        if not os.path.exists(configdir):
            log.info("Config dir doesn't existing, creating it...")
            os.makedirs(configdir)
        configpath = os.path.join(configdir, "settings.json")
        self.__config = config = easysettings.load_json_settings(
            configpath,
            default={
                "theme": "System",
                "geometry": self.centre_position,
                "out_mode": False,
                "locale": "en",
                "recents": [],
                "show_get_last_error": True,
                "show_errno": True,
            },
        )
        if lang:
            locale_to_use = lang
            self.__dont_save_locale = True
        else:
            locale_to_use = config["locale"]
        if out_mode:
            out_mode_or_not = True
            self.__dont_save_out_mode = True
        else:
            out_mode_or_not = config["out_mode"]
        if hide_last_err:
            show_get_last_error = False
            self.__dont_save_show_get_last_error = True
        else:
            show_get_last_error = config["show_get_last_error"]
        if hide_errno:
            show_errno = False
            self.__dont_save_show_errno = True
        else:
            show_errno = config["show_errno"]
        self.__recents.extend(config["recents"])

        # ! BUG: Tkinter doesn't understand Windows paths
        msgs_path = os.path.join(dirpath, "msgs").replace("\\", "/")

        # * The order and place where these 2 are called is very important
        log.debug("Loading message catalogs from %s", msgs_path)
        found = MsgCat.load(msgs_path)
        log.debug("Found %d translation files", found)
        MsgCat.locale(locale_to_use)

        self.arch = platform.architecture()[0]
        self.title(self.__default_title)
        self.minsize(width=450, height=600)
        set_app_icon(self)
        self.cur_theme = tk.StringVar(value=config["theme"])

        # Set by picker
        self.lib = None

        # Modern menus
        self.option_add("*tearOff", False)

        self.__is_native = tk.BooleanVar()
        self.__is_running = tk.BooleanVar(value=False)
        self.__is_loaded = tk.BooleanVar(value=False)
        self.__is_reinitialised = tk.BooleanVar(value=False)
        self.__use_out_mode = tk.BooleanVar(value=out_mode_or_not)
        self.__locale = tk.StringVar(value=locale_to_use)
        self.__sort_order = tk.StringVar(value=SortOrder.NameAscending.value)
        self.__library_path = tk.StringVar(value=lib)
        self.__selected_export = tk.StringVar(value=exp)
        self.__call_convention = tk.StringVar(value=conv)
        self.__return_type = tk.StringVar(value=ret)
        self.__output_text = tk.StringVar()
        self.__status_text = tk.StringVar(value="Choose a library")
        self.__exc_type = tk.StringVar()
        self.__get_last_error = tk.IntVar()
        self.__show_get_last_error = tk.BooleanVar(value=show_get_last_error)
        self.__errno = tk.IntVar()
        self.__show_errno = tk.BooleanVar(value=show_errno)

        # Events
        # ! Always use `self.__parent.event_generate`
        self.event_add("<<LanguageChanged>>", "None")
        self.event_add("<<OutputSuccess>>", "None")
        self.event_add("<<OutputException>>", "None")
        self.event_add("<<PopulateExports>>", "None")
        self.event_add("<<SortExports>>", "None")
        self.event_add("<<ToggleErrno>>", "None")
        self.event_add("<<ToggleExportsFrame>>", "None")
        self.event_add("<<ToggleFunctionFrame>>", "None")
        self.event_add("<<ToggleGetLastError>>", "None")
        self.event_add("<<UpdateRecents>>", "None")
        self.bind_all("<<LanguageChanged>>", lambda *_: self.refresh())

        # Control variable traces
        self.__show_get_last_error.trace_add(
            "write", lambda *_: self.event_generate("<<ToggleGetLastError>>")
        )
        self.__show_errno.trace_add(
            "write", lambda *_: self.event_generate("<<ToggleErrno>>")
        )

        self.geometry(config["geometry"])
        self.deiconify()
        self.set_theme()
        self.init_widgets()
        log.debug("App initialised")

    @property
    def __default_title(self) -> str:
        return f"DyCall ({self.arch})"

    def init_widgets(self):
        """Sub-widgets are created and packed here.

        Separated from `__init__` because `refresh` requires this method too.
        These widgets are purposely public to allow subframes to access each
        other's widgets through their `parent` attribute when necessary. The
        order in which they get constructed is essential, it must be ensured
        that no widget constructed first depends internally on a widget
        constructed later here.
        """
        self.output = of = OutputFrame(
            self,
            self.__output_text,
            self.__exc_type,
        )
        self.status_bar = sf = StatusBarFrame(
            self,
            self.__status_text,
            self.__get_last_error,
            self.__show_get_last_error,
            self.__errno,
            self.__show_errno,
        )
        self.function = ff = FunctionFrame(
            self,
            self.__call_convention,
            self.__return_type,
            self.__library_path,
            self.__selected_export,
            self.__output_text,
            self.__status_text,
            self.__use_out_mode,
            self.__is_running,
            self.__exc_type,
            self.__get_last_error,
            self.__show_get_last_error,
            self.__errno,
            self.__show_errno,
            self.__rows_to_add,
        )
        self.exports = ef = ExportsFrame(
            self,
            self.__selected_export,
            self.__sort_order,
            self.__output_text,
            self.__status_text,
            self.__is_loaded,
            self.__is_native,
            self.__is_reinitialised,
            self.__exports,
        )
        self.picker = pf = PickerFrame(
            self,
            self.__library_path,
            self.__selected_export,
            self.__output_text,
            self.__status_text,
            self.__is_loaded,
            self.__is_native,
            self.__default_title,
            self.__exports,
            self.__recents,
        )
        self.top_menu = tm = TopMenu(
            self,
            self.__use_out_mode,
            self.__locale,
            self.__sort_order,
            self.__show_get_last_error,
            self.__show_errno,
            self.__recents,
        )

        pf.pack(fill="x", padx=5)
        ef.pack(fill="x", padx=5)
        ff.pack(fill="both", expand=True)  # Padding handled by the frame
        of.pack(fill="x", padx=5)
        sf.pack(fill="x")
        self["menu"] = tm

    def refresh(self):
        """Called when the interace language is changed to reflect the changes.

        TtkBootstrap doesn't let me destroy and reinitialise `App` so I found
        out this cool solution. Sets reinitalised flag so that re-demangling is
        prevented in `self.exports`.
        """
        self.__is_reinitialised.set(True)
        self.top_menu.destroy()
        self.picker.destroy()
        self.exports.destroy()
        self.function.destroy()
        self.output.destroy()
        self.status_bar.destroy()
        self.set_theme()
        self.init_widgets()

    def destroy(self):
        """Warns the user if he tries to close when an operation is running.
        Tries to save the app settings and proceeds to close the app.
        """  # noqa: D205
        # ! This does't work at all
        is_running = self.__is_running.get()
        log.debug("Called with is_running=%s", is_running)
        if self.__is_running.get():
            if (
                Messagebox.show_question(
                    "An operation is running, do you really want to quit?",
                    buttons=("No:primary", "Yes:danger"),
                )
                != "Yes"
            ):
                return

        config = self.__config
        config["theme"] = self.cur_theme.get()
        config["geometry"] = self.geometry()
        config["recents"] = tuple(self.__recents)
        if not self.__dont_save_out_mode:
            config["out_mode"] = self.__use_out_mode.get()
        if not self.__dont_save_locale:
            config["locale"] = self.__locale.get()
        if not self.__dont_save_show_get_last_error:
            config["show_get_last_error"] = self.__show_get_last_error.get()
        if not self.__dont_save_show_errno:
            config["show_errno"] = self.__show_errno.get()
        try:
            config.save()
        except IOError as e:
            result = Messagebox.retrycancel(
                f"Failed to save config file due to {repr(e)}",
                "Error",
                parent=self,
                icon=Icon.error,
            )
            if result == "Retry":
                self.destroy()
        super().destroy()

    @property
    def centre_position(self):
        w_height = self.winfo_height()
        w_width = self.winfo_width()
        s_height = self.winfo_screenheight()
        s_width = self.winfo_screenwidth()
        xpos = (s_width - w_width) // 2
        ypos = (s_height - w_height) // 2
        return f"+{xpos}+{ypos}"

    def set_theme(self):
        """Set's the theme used by DyCall."""
        log.debug("Setting theme")

        theme = self.cur_theme.get()
        if theme == "System":
            theme = darkdetect.theme()  # pylint: disable=assignment-from-none

        if theme == "Light":
            self.style.theme_use(LIGHT_THEME)
        elif theme == "Dark":
            self.style.theme_use(DARK_THEME)

        log.debug("Theme '%s' set", theme)
