#!/usr/bin/env python3

"""
dycall.types
~~~~~~~~~~~~

Most analogous to the "Model" part of the MVC design pattern.
"""

from __future__ import annotations

import abc
import dataclasses
import enum
import typing
from ctypes import (
    c_bool,
    c_char,
    c_char_p,
    c_double,
    c_float,
    c_int8,
    c_int16,
    c_int32,
    c_int64,
    c_uint8,
    c_uint16,
    c_uint32,
    c_uint64,
    c_void_p,
    c_wchar,
    c_wchar_p,
)
from typing import Any, Union

try:
    from typing import Final  # type: ignore
except ImportError:
    # pylint: disable=ungrouped-imports
    from typing_extensions import Final  # type: ignore

from dycall.util import DemangleError, demangle

_CType = Union[
    c_bool,
    c_char,
    c_char_p,
    c_double,
    c_float,
    c_int8,
    c_int16,
    c_int32,
    c_int64,
    c_uint8,
    c_uint16,
    c_uint32,
    c_uint64,
    None,
    c_void_p,
    c_wchar,
    c_wchar_p,
]

_StrToCtype = {
    "bool": c_bool,
    "char": c_char,
    "char*": c_char_p,
    "double": c_double,
    "float": c_float,
    "int8_t": c_int8,
    "int16_t": c_int16,
    "int32_t": c_int32,
    "int64_t": c_int64,
    "uint8_t": c_uint8,
    "uint16_t": c_uint16,
    "uint32_t": c_uint32,
    "uint64_t": c_uint64,
    "void": c_void_p,
    "void*": c_void_p,
    "wchar_t": c_wchar,
    "wchar_t*": c_wchar_p,
}


class ParameterType(enum.Enum):
    """Member names mimic format specifiers from `struct` module."""

    bool_ = "bool"
    """C99/C++ bool type. Note: Use `u32` for Win32 BOOL type."""

    c = "char"
    """A single ASCII character."""

    pc = "char*"
    """Null terminated ASCII string."""

    f = "float"
    """32-bit floating point integer."""

    d = "double"
    """64-bit floating point integer. Analogous to `double`"""

    b = "int8_t"
    """8-bit signed integer. Analogous to: `signed char`, `int8_t` and `SBYTE`."""

    h = "int16_t"
    """16-bit signed integer. Analogous to `signed short` and `int16_t`."""

    i = "int32_t"
    """32-bit signed integer. Analogous to `int32_t`, `DWORD` and `int`."""

    q = "int64_t"
    """64-bit signed integer. Analogous to `int64_t`, `__int64` and `long long`."""

    B = "uint8_t"
    """8-bit unsigned integer. Analogous to `uint8_t`, `BYTE` and `char`."""

    H = "uint16_t"
    """16-bit unsigned integer. Analogous to `uint16_t`, `WORD` and `wchar_t`."""

    I = "uint32_t"
    """32-bit unsigned integer. Analogous to `uint32_t`, `DWORD` and `unsigned int`."""

    Q = "uint64_t"
    """64-bit unsigned integer. Analogous to `uint64_t` and `unsigned long long`."""

    v = "void"
    """Void return type."""

    pv = "void*"
    """Any other custom type or a type not in `ParameterType`."""

    w = "wchar_t"
    """A single UTF-16 character."""

    pw = "wchar_t*"
    """Null terminated UTF-16 string."""

    @property
    def ctype(self):
        """Returns equivalent ctypes data type."""
        return _StrToCtype[self.value]


PARAMETER_TYPES: Final = tuple(t.value for t in ParameterType)


class CallConvention(enum.Enum):
    """Calling convention to use when calling a function.

    Since, Linux libs don't use stdcall, this is required only for Windows.
    """

    Cdecl = "cdecl"
    """Commonly used on all platforms. Most probably you will need this."""

    StdCall = "stdcall"
    """More popular on Windows, all system libraries on Windows use this."""


CALL_CONVENTIONS: Final = tuple(t.value for t in CallConvention)


class Marshaller:
    """Common converter methods for Tkinter <-> Python <-> ctypes interop."""

    @staticmethod
    def ctype2str(p: _CType) -> str:
        """Ctypes -> Tkinter."""
        v = "NULL"
        if p is not None:
            val = p.value
            if isinstance(p, c_bool):
                v = "True" if val else "False"
            elif isinstance(p, (c_char, c_char_p)):
                if typing.TYPE_CHECKING:
                    assert isinstance(val, bytes)  # nosec
                v = val.decode("utf-8", errors="replace")
            else:
                v = str(val)
        return v

    @staticmethod
    def pytype2str(p: Any) -> str:
        """Python -> Tkinter."""
        if p:
            if isinstance(p, bytes):
                return p.decode("utf-8", errors="replace")
            return str(p)
        return "NULL"

    @typing.no_type_check
    @staticmethod
    def str2ctype(t: _CType, val: str) -> _CType:
        """Tkinter -> ctypes."""
        # pylint: disable=no-else-return
        if t in (
            c_int8,
            c_int16,
            c_int32,
            c_int64,
            c_uint8,
            c_uint16,
            c_uint32,
            c_uint64,
        ):
            return t(int(val))
        elif t in (c_double, c_float):
            return t(float(val))
        elif t in (c_char, c_char_p):
            return t(val.encode("utf-8"))  # or ascii?
        elif t in (c_wchar, c_wchar_p):
            return t(val)
        return None


@dataclasses.dataclass
class RunResult:
    """Returned by `Runner` back to UI. This is useful especially in **OUT Mode**."""

    ret: _CType
    args: tuple[_CType] = dataclasses.field(default_factory=tuple)  # type: ignore

    @property
    def values(self) -> list[Any]:
        """Ctypes -> Tkinter representation for all arguments."""
        values = []
        for arg in self.args:
            v = Marshaller.ctype2str(arg)
            values.append(v)
        return values


class SortOrder(enum.Enum):
    """Export name sort order in **Exports** combobox."""

    NameAscending = "Name (ascending)"
    NameDescending = "Name (descending)"


@dataclasses.dataclass
class Export(abc.ABC):
    """Constains all the required information about an exported function.

    LIEF doesn't provide a standard platform-independent way to get this
    information. Its better to have a DyCall-specific type; also it is
    used almost everywhere.
    """

    address: int
    """See `lief.Function.address`."""

    name: str
    """See `lief.Function.name`."""


@dataclasses.dataclass
class PEExport(Export):
    """Represents a Windows library export."""

    ordinal: int
    """See `lief.PE.ExportEntry.ordinal`."""

    def __post_init__(self):
        """Calculate a demangled/displayed name."""
        if self.name:
            try:
                self.demangled_name = demangle(self.name)
            except DemangleError as exc:
                self.exc = exc
        else:
            # Ordinal-only exports
            self.demangled_name = f"@{self.ordinal}"


@dataclasses.dataclass
class ELFExport(Export):
    """Represents a Linux or MacOS library export."""

    demangled_name: str
    """See `lief.ELF.Symbol.demangled_name`."""
