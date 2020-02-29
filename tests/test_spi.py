#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.interface.serial.spi` class.
"""

import pytest
from unittest.mock import Mock, call

from luma.core.interface.serial import spi
import luma.core.error

from helpers import get_spidev, rpi_gpio_missing, fib


spidev = Mock(unsafe=True)
gpio = Mock(unsafe=True)


def setup_function(function):
    spidev.reset_mock()
    gpio.reset_mock()
    gpio.BCM = 1
    gpio.RST = 2
    gpio.DC = 3
    gpio.OUT = 4
    gpio.HIGH = 5
    gpio.LOW = 6


def verify_spi_init(port, device, bus_speed_hz=8000000, dc=24, rst=25):
    spidev.open.assert_called_once_with(port, device)
    assert spidev.max_speed_hz == bus_speed_hz
    gpio.setmode.assert_not_called()
    gpio.setup.assert_has_calls([call(dc, gpio.OUT), call(rst, gpio.OUT)])


def test_init():
    port = 5
    device = 2
    bus_speed = 16000000
    dc = 17
    rst = 11

    spi(gpio=gpio, spi=spidev, port=port, device=device, bus_speed_hz=16000000,
        gpio_DC=dc, gpio_RST=rst)
    verify_spi_init(port, device, bus_speed, dc, rst)
    gpio.output.assert_has_calls([
        call(rst, gpio.LOW),
        call(rst, gpio.HIGH)
    ])


def test_init_invalid_bus_speed():
    with pytest.raises(AssertionError):
        spi(gpio=gpio, spi=spidev, port=5, device=2, bus_speed_hz=942312)


def test_command():
    cmds = [3, 1, 4, 2]
    serial = spi(gpio=gpio, spi=spidev, port=9, device=1)
    serial.command(*cmds)
    verify_spi_init(9, 1)
    gpio.output.assert_has_calls([call(25, gpio.HIGH), call(24, gpio.LOW)])
    spidev.writebytes.assert_called_once_with(cmds)


def test_data():
    data = list(fib(100))
    serial = spi(gpio=gpio, spi=spidev, port=9, device=1)
    serial.data(data)
    verify_spi_init(9, 1)
    gpio.output.assert_has_calls([call(25, gpio.HIGH), call(24, gpio.HIGH)])
    spidev.writebytes.assert_called_once_with(data)


def test_cleanup():
    serial = spi(gpio=gpio, spi=spidev, port=9, device=1)
    serial._managed = True
    serial.cleanup()
    verify_spi_init(9, 1)
    spidev.close.assert_called_once_with()
    gpio.cleanup.assert_called_once_with()


def test_init_device_not_found():
    spidev = get_spidev()
    port = 1234
    with pytest.raises(luma.core.error.DeviceNotFoundError) as ex:
        spi(gpio=gpio, spi=spidev.SpiDev(), port=port)
    assert str(ex.value) == 'SPI device not found'


def test_unsupported_gpio_platform():
    try:
        spi(spi=spidev, port=9, device=1)
    except luma.core.error.UnsupportedPlatform as ex:
        assert str(ex) == 'GPIO access not available'
    except ImportError:
        pytest.skip(rpi_gpio_missing)
