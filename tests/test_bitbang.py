#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.interface.serial.bitbang` class.
"""

from unittest.mock import Mock, call
from luma.core.interface.serial import bitbang
import luma.core.error

import pytest

from helpers import rpi_gpio_missing


gpio = Mock(unsafe=True)


def setup_function(function):
    gpio.reset_mock()
    gpio.BCM = 1
    gpio.RST = 2
    gpio.DC = 3
    gpio.OUT = 4
    gpio.HIGH = 5
    gpio.LOW = 6


def test_data():
    data = (0xFF, 0x0F, 0x00)
    serial = bitbang(gpio=gpio, SCLK=13, SDA=14, CE=15, DC=16, RST=17)
    serial.data(data)

    reset = [call(17, gpio.LOW), call(17, gpio.HIGH)]
    clock = [call(13, gpio.HIGH), call(13, gpio.LOW)]
    data = lambda x: call(14, 0x80 if x == gpio.HIGH else 0x00)
    ce = lambda x: [call(15, x)]
    dc = lambda x: [call(16, x)]

    calls = reset + \
        dc(gpio.HIGH) + \
        ce(gpio.LOW) + \
        (([data(gpio.HIGH)] + clock) * 8) + \
        (([data(gpio.LOW)] + clock) * 4) + \
        (([data(gpio.HIGH)] + clock) * 4) + \
        (([data(gpio.LOW)] + clock) * 8) + \
        ce(gpio.HIGH)

    gpio.output.assert_has_calls(calls)


def test_cleanup():
    serial = bitbang(gpio=gpio)
    serial._managed = True
    serial.cleanup()
    gpio.cleanup.assert_called_once_with()


def test_unsupported_gpio_platform():
    try:
        bitbang()
    except luma.core.error.UnsupportedPlatform as ex:
        assert str(ex) == 'GPIO access not available'
    except ImportError:
        pytest.skip(rpi_gpio_missing)
