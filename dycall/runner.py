#!/usr/bin/env python3

"""
dycall.runner
~~~~~~~~~~~~~

Contains `Runner`.
"""

from __future__ import annotations

import ctypes
import logging
import platform
import queue
import threading
from typing import Union

import ttkbootstrap as tk

from dycall.types import CallConvention, Marshaller, ParameterType, RunResult

log = logging.getLogger(__name__)


class Runner(threading.Thread):
    """Executes an exported function in a separate thread.

    Used in `FunctionFrame`. Exceptions and results are pushed into a queue.
    The queues are then checked regularly until they are not empty in the UI
    thread. This ensures that the UI doesn't get blocked.
    """

    def __init__(
        self,
        exc: queue.Queue,
        que: queue.Queue,
        args: list[list[str]],
        call_conv: str,
        returns: str,
        lib_path: str,
        name_or_ord: str,
        get_last_error: tk.IntVar,
        show_get_last_error: bool,
        errno: tk.IntVar,
        show_errno: bool,
    ) -> None:
        log.debug(
            "Called with args=%s, "
            "call_conv=%s, "
            "returns=%s, "
            "lib_path=%s, "
            "name_or_ord=%s, "
            "get_last_error=%d, "
            "show_get_last_error=%s, "
            "errno=%d, "
            "show_errno=%s",
            args,
            call_conv,
            returns,
            lib_path,
            name_or_ord,
            get_last_error.get(),
            show_get_last_error,
            errno.get(),
            show_errno,
        )
        self.__exc = exc
        self.__queue = que
        self.__get_last_error = get_last_error
        self.__show_get_last_error = show_get_last_error
        self.__errno = errno
        self.__show_errno = show_errno
        self.__is_windows = platform.system() == "Windows"
        self.__call_conv = CallConvention(call_conv)
        self.__restype = ParameterType(returns).ctype
        if self.__call_conv == CallConvention.StdCall:
            self.__handle = ctypes.WinDLL(
                lib_path,
                use_last_error=show_get_last_error,
                use_errno=show_errno,
            )
            self.__functype = ctypes.WINFUNCTYPE
        else:
            if self.__is_windows:
                self.__handle = ctypes.CDLL(  # type: ignore
                    lib_path,
                    use_errno=show_errno,
                    use_last_error=show_get_last_error,
                )
            else:
                self.__handle = ctypes.CDLL(  # type: ignore
                    lib_path, use_errno=show_errno
                )
            self.__functype = ctypes.CFUNCTYPE
        if name_or_ord.startswith("@"):
            self.__name_or_ord = int(name_or_ord[1:])  # type: Union[str, int]
        else:
            self.__name_or_ord = name_or_ord
        self.__argtypes = []
        self.__argvalues = []
        for arg in args:
            type_, value = arg
            argtype = ParameterType(type_).ctype
            argvalue = Marshaller.str2ctype(argtype, value)
            self.__argtypes.append(argtype)
            self.__argvalues.append(argvalue)
        super().__init__()

    def run(self):
        """Calculates the function prototype and operates with the queues."""
        try:
            if self.__argtypes:
                prototype = self.__functype(self.__restype, *self.__argtypes)
            else:
                prototype = self.__functype(self.__restype)
            ptr = prototype((self.__name_or_ord, self.__handle))
            result = ptr(*self.__argvalues)
            run_result = RunResult(result, self.__argvalues)
        except Exception as e:  # pylint: disable=broad-except
            self.__exc.put(e)
        else:
            self.__queue.put(run_result)
        # This is thread safe, see https://stackoverflow.com/a/25352087
        if self.__show_get_last_error and self.__is_windows:
            # ! ctypes.get_last_error() doesn't work
            gle = int(ctypes.windll.kernel32.GetLastError())
            log.debug("GetLastError - %d", gle)
            self.__get_last_error.set(gle)
        if self.__show_errno:
            errno = ctypes.get_errno()
            log.debug("errno - %d", errno)
            self.__errno.set(errno)
