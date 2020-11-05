# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

import luma.core.error


__all__ = ["rpi_gpio", "spidev"]


def __spidev__(self):  # pragma: no cover
    """
    Return an array of spidev : spide object

    Args:
        self: (todo): write your description
    """
    # spidev cant compile on macOS, so use a similar technique to
    # initialize (mainly so the tests run unhindered)
    import spidev
    return spidev.SpiDev()


def __rpi_gpio__(self):
    """
    Returns the gpio rpi.

    Args:
        self: (todo): write your description
    """
    # RPi.GPIO _really_ doesn't like being run on anything other than
    # a Raspberry Pi... this is imported here so we can swap out the
    # implementation for a mock
    try:  # pragma: no cover
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        return GPIO
    except RuntimeError as e:
        if str(e) in ['This module can only be run on a Raspberry Pi!',
                      'Module not imported correctly!']:
            raise luma.core.error.UnsupportedPlatform(
                'GPIO access not available')


def rpi_gpio(Class):
    """
    A decorator for a class.

    Args:
        Class: (todo): write your description
    """
    setattr(Class, __rpi_gpio__.__name__, __rpi_gpio__)
    return Class


def spidev(Class):
    """
    Returns a spide class.

    Args:
        Class: (todo): write your description
    """
    setattr(Class, __spidev__.__name__, __spidev__)
    return Class
