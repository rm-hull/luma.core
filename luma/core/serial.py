# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Encapsulates sending commands and data over a serial interface, whether that
is I²C, SPI or bit-banging GPIO.

This module is deprecated and will be removed in luma.core v1.0.0: use
:py:mod:`luma.core.interface.serial` instead.
"""

from luma.core.util import deprecation
from luma.core.interface.serial import i2c, spi, bitbang, noop, __all__  # noqa: F401


deprecation('luma.core.serial is deprecated and will be removed in v1.0.0: ' +
    'use luma.core.interface.serial instead')
