from __future__ import annotations

import logging
import queue
import threading
from ctypes import CDLL, CFUNCTYPE, WINFUNCTYPE, WinDLL

from dycall.types import CallConvention, Marshaller, ParameterType, RunResult

log = logging.getLogger(__name__)


class Runner(threading.Thread):
    def __init__(
        self,
        exc: queue.Queue,
        que: queue.Queue,
        args: list[list[str]],
        call_conv: str,
        returns: str,
        lib_path: str,
        funcname: str,
    ) -> None:
        log.debug(
            "Called with args={}, call_conv={}, returns={}, lib_path={}, funcname={}",
            args,
            call_conv,
            returns,
            lib_path,
            funcname,
        )
        self.__exc = exc
        self.__queue = que
        self.__call_conv = CallConvention(call_conv)
        self.__restype = ParameterType(returns).ctype
        if self.__call_conv == CallConvention.StdCall:
            self.__handle = WinDLL(lib_path)
            self.__functype = WINFUNCTYPE
        else:
            self.__handle = CDLL(lib_path)
            self.__functype = CFUNCTYPE
        self.__funcname = funcname
        self.__parse_args(args)
        super().__init__()

    def __parse_args(self, args: list[list[str]]) -> None:
        self.__argtypes = []
        self.__argvalues = []
        for arg in args:
            type_, value = arg
            argtype = ParameterType(type_).ctype
            argvalue = Marshaller.str2ctype(argtype, value)
            self.__argtypes.append(argtype)
            self.__argvalues.append(argvalue)

    def run(self):
        try:
            if self.__argtypes:
                prototype = self.__functype(self.__restype, *self.__argtypes)
            else:
                prototype = self.__functype(self.__restype)
            ptr = prototype((self.__funcname, self.__handle))
            result = ptr(*self.__argvalues)
            run_result = RunResult(result, self.__argvalues)
        except Exception as e:  # pylint: disable=broad-except
            self.__exc.put(e)
        else:
            self.__queue.put(run_result)
