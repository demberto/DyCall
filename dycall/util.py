# -*- coding: utf-8 -*-
from __future__ import annotations

import pathlib
import platform
from ctypes import create_unicode_buffer
from typing import Union

try:
    from ctypes import windll  # pylint: disable=ungrouped-imports
except ImportError:
    pass

try:
    from typing import Final  # type: ignore    # pylint: disable-next=ungrouped-imports
except ImportError:
    from typing_extensions import Final  # type: ignore

import cxxfilt
import ttkbootstrap as tk
from ttkbootstrap import ttk

# * Demangling

os = platform.system()
BUFSIZE: Final = 1000  # That should probably be enough


class DemangleError(Exception):
    """Raised when demangling fails due to an invalid name or an internal error."""


class PlatformUnsupportedError(Exception):
    """Raised when the OS is neither Windows nor has a libc and libcxx library."""


def demangle(exp: str) -> str:
    """On Linux & MacOS, cxxfilt is used, which internally uses `libcxx.__cxa_demangle`.

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
    try:
        return cxxfilt.demangle(exp)
    except cxxfilt.LibraryNotFound as e:
        raise PlatformUnsupportedError from e
    except OSError as e:
        raise DemangleError from e


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


# * Translations

# ! Translators should add the LCID and native form of the language below
LCID2Lang: Final = {"en": "English", "hi": "हिन्दी", "mr": "मराठी"}

LCIDS: Final = tuple(LCID2Lang.keys())

# Dictionary inversion: https://stackoverflow.com/a/66464410
Lang2LCID: Final = {v: k for k, v in LCID2Lang.items()}

# * Helpers

# https://stackoverflow.com/a/3430395
dirpath = pathlib.Path(__file__).parent.resolve()


def set_app_icon(wnd: Union[tk.Window, tk.Toplevel]):
    """Used by `App` and `DemanglerWindow` to set the window icon.

    Args:
        wnd: (Union[tk.Window, tk.Toplevel]): The window whose icon is to be set.
    """
    if platform.system() == "Windows":
        ico = dirpath / "img/dycall.ico"
        wnd.iconbitmap(ico)
    else:
        png = dirpath / "img/dycall.png"
        with open(png, "rb") as fp:
            img = tk.PhotoImage(data=fp.read())
        wnd.iconphoto(False, img)
