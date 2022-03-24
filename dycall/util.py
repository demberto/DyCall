# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
import pathlib
import platform
from ctypes import create_unicode_buffer
from typing import Callable, Union

import tktooltip

try:
    from ctypes import windll  # pylint: disable=ungrouped-imports
except ImportError:
    pass

try:
    from typing import Final  # type: ignore    # pylint: disable-next=ungrouped-imports
except ImportError:
    from typing_extensions import Final  # type: ignore

import ttkbootstrap as tk
from ttkbootstrap import ttk

log = logging.getLogger(__name__)

# * Demangling

os = platform.system()
BUFSIZE: Final = 1000  # That should probably be enough


class DemangleError(Exception):
    """Raised when demangling fails due to an invalid name or an internal error."""


def demangle(exp: str) -> str:
    """On Linux & MacOS, LIEF already provides the demangled name.

    On Windows, the DbgHelp API function `UnDecorateSymbolNameW` is used.
    MSDN: https://docs.microsoft.com/windows/win32/api/dbghelp/nf-dbghelp-undecoratesymbolnamew
    """  # noqa: E501
    if os == "Windows":
        if exp.startswith("?"):
            buf = create_unicode_buffer(BUFSIZE)
            try:
                hr = windll.dbghelp.UnDecorateSymbolNameW(exp, buf, BUFSIZE, 0)
            except OSError as e:
                raise DemangleError from e
            if hr:
                return buf.value
            raise DemangleError
    return exp


# * Constants

LIGHT_THEME: Final = "yeti"
DARK_THEME: Final = "darkly"

# * Custom widgets


class CopyButton(ttk.Button):  # pylint: disable=too-many-ancestors
    def __init__(self, parent: tk.Window, copy_from: tk.StringVar, *args, **kwargs):
        self.__copy_var = copy_from
        super().__init__(
            parent, text="⧉", command=self.copy, style="info-outline", *args, **kwargs
        )

    def copy(self, *_):
        self.clipboard_clear()
        self.clipboard_append(self.__copy_var.get())


class StaticThemedTooltip(tktooltip.ToolTip):
    def __init__(
        self,
        widget: tk.tk.Widget,
        parent: tk.Window,
        msg: Union[str, Callable] = None,
        delay: float = 1,
    ):
        fg = bg = None
        if parent.style.theme_use() == DARK_THEME:
            fg = "#ffffff"
            bg = "#1c1c1c"
        super().__init__(
            widget=widget,
            msg=msg,
            delay=delay,
            follow=False,
            fg=fg,
            bg=bg,
        )


# * Translations

# ! Translators should add the LCID and native form of the language below
LCID2Lang: Final = {"en": "English", "hi": "हिन्दी", "mr": "मराठी"}

LCIDS: Final = tuple(LCID2Lang.keys())

# Dictionary inversion: https://stackoverflow.com/a/66464410
Lang2LCID: Final = {v: k for k, v in LCID2Lang.items()}

# * Helpers

# https://stackoverflow.com/a/3430395
dirpath = pathlib.Path(__file__).parent.resolve()


def get_png(name: str, **kwargs) -> tk.PhotoImage:
    """Finds an image `name` in *img/* and returns a PhotoImage object.

    Additional keyword arguments are passed to `tk.PhotoImage`'s constructor.

    Args:
        name (str): The name of the image file as saved in *img/*, e.g. `clock.png`.
    """
    log.debug("Getting image %s", name)
    with open(dirpath / "img" / name, "rb") as png:
        return tk.PhotoImage(data=png.read(), **kwargs)


def set_app_icon(wnd: Union[tk.Window, tk.Toplevel]) -> None:
    """Used by `App` and `DemanglerWindow` to set the window icon.

    Args:
        wnd: (Union[tk.Window, tk.Toplevel]): The window whose icon is to be set.
    """
    log.debug("Setting app icon")
    if platform.system() == "Windows":
        ico = dirpath / "img/dycall.ico"
        wnd.iconbitmap(ico)
    else:
        wnd.iconphoto(False, get_png("dycall.png"))
