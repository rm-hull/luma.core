# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

from functools import wraps

import luma.core.error


__all__ = ["rpi_gpio", "spidev"]


def __spidev__(self):
    # spidev cant compile on macOS, so use a similar technique to
    # initialize (mainly so the tests run unhindered)
    import spidev
    return spidev.SpiDev()


def __rpi_gpio__(self):
    # RPi.GPIO _really_ doesn't like being run on anything other than
    # a Raspberry Pi... this is imported here so we can swap out the
    # implementation for a mock
    try:
        import RPi.GPIO
        return RPi.GPIO
    except RuntimeError as e:
        if str(e) in ['This module can only be run on a Raspberry Pi!',
                      'Module not imported correctly!']:
            raise luma.core.error.UnsupportedPlatform(
                'GPIO access not available')


def rpi_gpio(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        f.__rpi_gpio__ = classmethod(__rpi_gpio__)
        return f(*args, **kwds)
    return wrapper


def spidev(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        f.__spidev__ = classmethod(__spidev__)
        return f(*args, **kwds)
    return wrapper
