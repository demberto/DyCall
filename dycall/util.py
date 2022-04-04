#!/usr/bin/env python3

"""
dycall.util
~~~~~~~~~~~

Contains:
- Demangling: Logic used by `dycall.types.PEExport`, `dycall.types.ELFExport`
  and `dycall.demangler.DemanglerWindow`.
- Constants: TtkBootstrap light and dark theme names.
- Custom widgets: A tooltip and a copy button.
- Helpers: Image path and PhotoImage object getters.
"""

from __future__ import annotations

import ctypes
import logging
import pathlib
import platform
from typing import Callable, Optional, Union

try:
    from typing import Final  # type: ignore
except ImportError:
    # pylint: disable=ungrouped-imports
    from typing_extensions import Final  # type: ignore

try:
    import cxxfilt
except ImportError:
    pass

import tktooltip
import ttkbootstrap as tk
from ttkbootstrap import ttk

log = logging.getLogger(__name__)

# * Demangling

os = platform.system()
BUFSIZE: Final = 1000  # That should probably be enough


class DemangleError(Exception):
    """Raised when demangling fails due to any reason."""


def demangle(exp: str) -> str:
    """On Linux & MacOS, LIEF already provides the demangled name.

    On Windows, the DbgHelp API function `UnDecorateSymbolNameW` is used.
    MSDN: https://docs.microsoft.com/windows/win32/api/dbghelp/nf-dbghelp-undecoratesymbolnamew
    """  # noqa: E501
    if os == "Windows":
        if exp.startswith("?"):
            buf = ctypes.create_unicode_buffer(BUFSIZE)
            try:
                dbghelp = ctypes.windll["dbghelp"]
                hr = dbghelp.UnDecorateSymbolNameW(exp, buf, BUFSIZE, 0)
            except OSError as e:
                raise DemangleError from e
            if hr:
                return buf.value
            raise DemangleError
        return exp
    try:
        return cxxfilt.demangle(exp)
    except cxxfilt.Error as e:
        raise DemangleError from e


# * Constants

LIGHT_THEME: Final = "yeti"
DARK_THEME: Final = "darkly"

# * Custom widgets


class CopyButton(ttk.Button):
    """Button which copies text from a `tk.StringVar` to system clipboard."""

    def __init__(self, parent: tk.Window, copy_from: tk.StringVar, *args, **kwargs):
        self.__copy_var = copy_from
        super().__init__(
            parent,
            text="⧉",
            command=lambda *_: self.copy(),
            style="info-outline",
            *args,
            **kwargs,
        )
        self.bind("<Enter>", lambda *_: StaticThemedTooltip(self, "Copy", delay=0.5))

    def copy(self):
        """Clears the clipboard and appends new text.

        Tkinter's clipboard system works a bit differently.
        """
        self.clipboard_clear()
        self.clipboard_append(self.__copy_var.get())


class StaticThemedTooltip(tktooltip.ToolTip):
    """A non-tracking theme-aware tooltip with a configurable delay."""

    def __init__(
        self,
        widget: tk.tk.Widget,
        msg: Union[str, Callable] = None,
        delay: float = 1,
    ):
        fg = bg = None
        if tk.Style().theme_use() == DARK_THEME:
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

SHOW_IMAGES = True
"""`get_img_path` and `get_img` return None when this is False.

Set to False when DyCall is run with the `--no-images` switch."""


class _ImageFinder:
    """DyCall image finder.

    Images are searched in the `img/` relative to the folder this file is in.
    I didn't quite like what `pkgutil` or `importlib.resources` had to offer.
    Images should never be loaded/searched without using this class or the
    helper methods `get_img` and `get_img_path`.
    """

    # https://stackoverflow.com/a/3430395
    _dirpath = pathlib.Path(__file__).parent.resolve()
    _imgpath: Final = _dirpath / "img"

    def __init__(self, name: str, **kwargs) -> None:
        self.__name = name
        self.__photo_image_kw = kwargs

    @property
    def path(self) -> str:
        """Returns the absolute path of the image.

        Use this only when `photo_image` is not an option.
        """
        log.debug("Getting path of image %s", self.__name)
        return str(self._imgpath / self.__name)

    @property
    def photo_image(self) -> tk.PhotoImage:
        """Returns the image as a `tk.PhotoImage` object.

        Use this whenever possible.
        """
        log.debug("Getting image object for %s", self.__name)
        with open(self._imgpath / self.__name, "rb") as img:
            return tk.PhotoImage(data=img.read(), **self.__photo_image_kw)


def get_img_path(name: str) -> Optional[str]:
    """Returns the absolute path of an image."""
    if SHOW_IMAGES:
        return _ImageFinder(name).path
    return None


def get_img(name: str, **kwargs) -> Optional[tk.PhotoImage]:
    """Returns an image as a `tk.PhotoImage` object.

    Args:
        name (str): File name of image.
        kwargs: Additional arguments passed directly to `tk.PhotoImage`.
    """
    if SHOW_IMAGES:
        return _ImageFinder(name, **kwargs).photo_image
    return None
