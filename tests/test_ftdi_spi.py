#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.interface.serial.ftdi_spi` class.
"""

from unittest.mock import Mock, call, patch
from luma.core.interface.serial import ftdi_spi
from helpers import fib


@patch('pyftdi.spi.SpiController')
def test_init(mock_controller):
    gpio = Mock()
    instance = Mock()
    instance.get_port = Mock()
    instance.get_gpio = Mock(return_value=gpio)
    mock_controller.side_effect = [instance]

    ftdi_spi(device='ftdi://dummy', bus_speed_hz=16000000, gpio_CS=3, gpio_DC=5, gpio_RST=6)
    mock_controller.assert_called_with(cs_count=1)
    instance.configure.assert_called_with('ftdi://dummy')
    instance.get_port.assert_called_with(cs=0, freq=16000000, mode=0)
    instance.get_gpio.assert_called_with()
    gpio.set_direction.assert_called_with(0x60, 0x60)


@patch('pyftdi.spi.SpiController')
def test_command(mock_controller):
    cmds = [3, 1, 4, 2]
    gpio = Mock()
    port = Mock()
    instance = Mock()
    instance.get_port = Mock(return_value=port)
    instance.get_gpio = Mock(return_value=gpio)
    mock_controller.side_effect = [instance]

    serial = ftdi_spi(device='ftdi://dummy', bus_speed_hz=16000000, gpio_CS=3, gpio_DC=5, gpio_RST=6)
    serial.command(*cmds)
    gpio.write.assert_has_calls([call(0x00), call(0x40), call(0x40)])
    port.write.assert_called_once_with(cmds)


@patch('pyftdi.spi.SpiController')
def test_data(mock_controller):
    data = list(fib(100))
    gpio = Mock()
    port = Mock()
    instance = Mock()
    instance.get_port = Mock(return_value=port)
    instance.get_gpio = Mock(return_value=gpio)
    mock_controller.side_effect = [instance]

    serial = ftdi_spi(device='ftdi://dummy', bus_speed_hz=16000000, gpio_CS=3, gpio_DC=5, gpio_RST=6)
    serial.data(data)
    gpio.write.assert_has_calls([call(0x00), call(0x40), call(0x60)])
    port.write.assert_called_once_with(data)


@patch('pyftdi.spi.SpiController')
def test_cleanup(mock_controller):
    gpio = Mock()
    port = Mock()
    instance = Mock()
    instance.get_port = Mock(return_value=port)
    instance.get_gpio = Mock(return_value=gpio)
    mock_controller.side_effect = [instance]

    serial = ftdi_spi(device='ftdi://dummy', bus_speed_hz=16000000, gpio_CS=3, gpio_DC=5, gpio_RST=6)
    serial.cleanup()
    instance.terminate.assert_called_once_with()
