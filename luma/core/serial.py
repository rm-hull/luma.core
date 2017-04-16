# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Encapsulates sending commands and data over a serial interface, whether that
is I²C, SPI or bitbanging GPIO.
"""

from luma.core.interface.serial import i2c, spi, bitbang, noop  # noqa: F401


__all__ = ["i2c", "spi", "bitbang"]
