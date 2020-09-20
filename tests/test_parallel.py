#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:module:`luma.core.interface.parallel` module.
"""

from unittest.mock import Mock, call
from luma.core.interface.parallel import bitbang_6800
import luma.core.error

import pytest

from helpers import rpi_gpio_missing


gpio = Mock(unsafe=True)


def setup_function(function):
    gpio.reset_mock()
    gpio.HIGH = 200
    gpio.LOW = 100
    gpio.RS = 7
    gpio.E = 8
    gpio.PINS = [25, 24, 23, 18]
    gpio.DATA = gpio.HIGH
    gpio.CMD = gpio.LOW
    gpio.OUT = 300


def test_data():
    eight_to_four = lambda data: [f(x) for x in data for f in (lambda x: x >> 4, lambda x: 0x0F & x)]

    data = (0x41, 0x42, 0x43)  # ABC
    serial = bitbang_6800(gpio=gpio, RS=7, E=8, PINS=[25, 24, 23, 18])

    serial.command(*eight_to_four([0x80]))
    serial.data(eight_to_four(data))

    setup = [call(gpio.RS, gpio.OUT), call(gpio.E, gpio.OUT)] + \
        [call(gpio.PINS[i], gpio.OUT) for i in range(4)]
    prewrite = lambda mode: [call(gpio.RS, mode), call(gpio.E, gpio.LOW)]
    pulse = [call(gpio.E, gpio.HIGH), call(gpio.E, gpio.LOW)]
    send = lambda v: [call(gpio.PINS[i], (v >> i) & 0x01) for i in range(serial._datalines)]

    calls = \
        prewrite(gpio.CMD) + send(0x08) + pulse + send(0x00) + pulse + \
        prewrite(gpio.DATA) + \
        send(data[0] >> 4) + pulse + \
        send(data[0]) + pulse + \
        send(data[1] >> 4) + pulse + \
        send(data[1]) + pulse + \
        send(data[2] >> 4) + pulse + \
        send(data[2]) + pulse

    gpio.setup.assert_has_calls(setup)
    gpio.output.assert_has_calls(calls)


def test_wrong_number_of_pins():
    try:
        bitbang_6800(gpio=gpio, RS=7, E=8, PINS=[25, 24, 23])
    except AssertionError as ex:
        assert str(ex) == 'You\'ve provided 3 pins but a bus must contain either four or eight pins'


def test_cleanup():
    serial = bitbang_6800(gpio=gpio)
    serial._managed = True
    serial.cleanup()
    gpio.cleanup.assert_called_once_with()


def test_unsupported_gpio_platform():
    try:
        bitbang_6800()
    except luma.core.error.UnsupportedPlatform as ex:
        assert str(ex) == 'GPIO access not available'
    except ImportError:
        pytest.skip(rpi_gpio_missing)
