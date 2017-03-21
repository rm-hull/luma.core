# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

import os
import sys
import time
import warnings
import ctypes.util


__all__ = ["deprecation", "monotonic"]


try:
    monotonic = time.monotonic
except AttributeError:
    try:
        clock_gettime = ctypes.CDLL(ctypes.util.find_library('c'),
                                    use_errno=True).clock_gettime
    except AttributeError:
        clock_gettime = ctypes.CDLL(ctypes.util.find_library('rt'),
                                    use_errno=True).clock_gettime

    class timespec(ctypes.Structure):
        """
        Time specification, as described in clock_gettime(3).
        """
        _fields_ = (('tv_sec', ctypes.c_long),
                    ('tv_nsec', ctypes.c_long))

    if sys.platform.startswith('linux'):
        CLOCK_MONOTONIC = 1
    elif sys.platform.startswith('freebsd'):
        CLOCK_MONOTONIC = 4
    elif sys.platform.startswith('sunos5'):
        CLOCK_MONOTONIC = 4
    elif 'bsd' in sys.platform:
        CLOCK_MONOTONIC = 3
    elif sys.platform.startswith('aix'):
        CLOCK_MONOTONIC = ctypes.c_longlong(10)

    def monotonic():
        """
        Monotonic clock, cannot go backward.
        """
        ts = timespec()
        if clock_gettime(CLOCK_MONOTONIC, ctypes.pointer(ts)):
            errno = ctypes.get_errno()
            raise OSError(errno, os.strerror(errno))
        return ts.tv_sec + ts.tv_nsec / 1.0e9


def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)
