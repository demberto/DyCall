import logging
import os
import platform

import appdirs
import darkdetect
import easysettings
import ttkbootstrap as tk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.icons import Icon
from ttkbootstrap.localization import MessageCatalog

from dycall.exports import ExportsFrame
from dycall.function import FunctionFrame
from dycall.output import OutputFrame
from dycall.picker import PickerFrame
from dycall.status_bar import StatusBarFrame
from dycall.top_menu import TopMenu

log = logging.getLogger(__name__)


class App(tk.Window):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        *args,
        conv: str = "",
        exp: str = "",
        lib: str = "",
        ret: str = "",
        rows: int = 0,
        lang: str = "",
        out_mode: bool = "",
        **kwargs,
    ) -> None:
        """DyCall entry point. Certain arguments can be passed from the command
        line directly. These arguments will be used to initalise the interface.
        This helps achieve some automation and it also saves my time while testing.
        The default arguments aren't the default values used by DyCall interface.

        Args:
            conv (str, optional): Calling convention. Defaults to "".
            exp (str, optional): Name of exported function. Defaults to "".
            lib (str, optional): Path/name of the library. Defaults to "".
            ret (str, optional): Return type. See `ParameterType`. Defaults to "".
            rows (int, optional): Number of empty rows to add to arguments table.
                Defaults to 0.
            lang (str, optional): _description_. Defaults to "".
        """

        log.debug("Initialising")
        self.rows_to_add = rows

        # No need to save a preference in the config when
        # DyCall is passed with it from the command line.
        self.__dont_save_locale = False
        self.__dont_save_out_mode = False

        super().__init__(*args, **kwargs)
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

        # * The order and place where these 2 are called is very important
        log.debug("Loading message catalogs")
        MessageCatalog.load("dycall/msgs")
        MessageCatalog.locale(locale_to_use)

        self.arch = platform.architecture()[0]
        self.title(self.default_title)
        self.minsize(width=450, height=600)
        self.iconbitmap("dycall/img/dycall.ico")
        self.cur_theme = tk.StringVar(value=config["theme"])

        # Set by picker
        self.lib = None

        # Modern menus
        self.option_add("*tearOff", False)

        self.is_native = tk.BooleanVar()
        self.is_running = tk.BooleanVar(value=False)
        self.use_out_mode = tk.BooleanVar(value=out_mode_or_not)
        self.locale = tk.StringVar(value=locale_to_use)
        self.library_path = tk.StringVar(value=lib)
        self.export_name = tk.StringVar(value=exp)
        self.call_convention = tk.StringVar(value=conv)
        self.return_type = tk.StringVar(value=ret)
        self.output_text = tk.StringVar()
        self.status_text = tk.StringVar(value="Choose a library")

        self.geometry(config["geometry"])
        self.deiconify()
        self.init_widgets()
        self.set_theme()
        log.debug("App initialised")

    @property
    def default_title(self) -> str:
        return f"DyCall ({self.arch})"

    def init_widgets(self):
        """Widgets are created and packed here. Separated from
        `__init__` because `refresh` requires this method too."""

        self.top_menu = tm = TopMenu(
            self,
            self.use_out_mode,
            self.locale,
        )
        self.output = of = OutputFrame(
            self,
            self.output_text,
        )
        self.status_bar = sf = StatusBarFrame(
            self,
            self.status_text,
        )
        self.function = ff = FunctionFrame(
            self,
            self.call_convention,
            self.return_type,
            self.library_path,
            self.export_name,
            self.output_text,
            self.status_text,
            self.use_out_mode,
            self.is_running,
            self.rows_to_add,
        )
        self.exports = ef = ExportsFrame(
            self,
            self.export_name,
            self.output_text,
            self.status_text,
            self.is_native,
        )
        self.picker = pf = PickerFrame(
            self,
            self.library_path,
            self.export_name,
            self.output_text,
            self.status_text,
            self.is_native,
            self.default_title,
        )

        pf.pack(fill="x", padx=5)
        ef.pack(fill="x", padx=5)
        ff.pack(fill="both", expand=True)  # Padding handled by the frame
        of.pack(fill="x", padx=5)
        sf.pack(fill="x")
        self["menu"] = tm

    def refresh(self):
        """Called when the interace language is changed to reflect back the changes.
        TtkBootstrap doesn't let me destroy and reinitialise `App` so I found out
        this cool solution."""

        self.top_menu.destroy()
        self.picker.destroy()
        self.exports.destroy()
        self.function.destroy()
        self.output.destroy()
        self.status_bar.destroy()
        self.init_widgets()
        self.set_theme(True)

    def destroy(self):
        """Warns the user if he tries to close when an operation is running.
        Tries to save the app settings and proceeds to close the app."""

        # ! This does't work at all
        is_running = self.is_running.get()
        log.debug("Called with is_running={}", is_running)
        if self.is_running.get():
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
        if not self.__dont_save_out_mode:
            config["out_mode"] = self.use_out_mode.get()
        if not self.__dont_save_locale:
            config["locale"] = self.locale.get()
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

    def set_theme(self, table_only=False):
        """Set's the theme used by DyCall. Used by `refresh` with `table_only`
        set to `True`, because reinitialising the widgets caused the table
        theme to be set again, rest of the widgets don't need this.

        Args:
            table_only (bool, optional): Defaults to False.
        """

        log.debug("Setting theme, table_only={}", table_only)

        def go_dark():
            if not table_only:
                self.style.theme_use("darkly")
            self.function.at.change_theme("dark blue")

        def go_light():
            if not table_only:
                self.style.theme_use("yeti")
            self.function.at.change_theme("light blue")

        theme = self.cur_theme.get()
        if theme == "System":
            theme = darkdetect.theme()  # pylint: disable=assignment-from-none

        if theme == "Light":
            go_light()
        elif theme == "Dark":
            go_dark()

        log.debug("Theme '{}' set", theme)
