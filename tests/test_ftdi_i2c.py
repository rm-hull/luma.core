#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019-2020 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.interface.serial.ftdi_i2c` class.
"""

import pytest
from unittest.mock import Mock, patch
from luma.core.interface.serial import ftdi_i2c
from helpers import fib
import luma.core.error


@patch('pyftdi.i2c.I2cController')
def test_init(mock_controller):
    instance = Mock()
    instance.get_port = Mock()
    mock_controller.side_effect = [instance]

    ftdi_i2c(device='ftdi://dummy', address='0xFF')
    mock_controller.assert_called_with()
    instance.configure.assert_called_with('ftdi://dummy')
    instance.get_port.assert_called_with(0xFF)


@patch('pyftdi.i2c.I2cController')
def test_command(mock_controller):
    cmds = [3, 1, 4, 2]
    port = Mock()
    instance = Mock()
    instance.get_port = Mock(return_value=port)
    mock_controller.side_effect = [instance]

    serial = ftdi_i2c(device='ftdi://dummy', address=0x3C)
    serial.command(*cmds)
    port.write_to.assert_called_once_with(0x00, cmds)


@patch('pyftdi.i2c.I2cController')
def test_data(mock_controller):
    data = list(fib(100))
    port = Mock()
    instance = Mock()
    instance.get_port = Mock(return_value=port)
    mock_controller.side_effect = [instance]

    serial = ftdi_i2c(device='ftdi://dummy', address=0x3C)
    serial.data(data)
    port.write_to.assert_called_once_with(0x40, data)


@patch('pyftdi.i2c.I2cController')
def test_cleanup(mock_controller):
    port = Mock()
    instance = Mock()
    instance.get_port = Mock(return_value=port)
    mock_controller.side_effect = [instance]

    serial = ftdi_i2c(device='ftdi://dummy', address=0x3C)
    serial.cleanup()
    instance.terminate.assert_called_once_with()


@patch('pyftdi.i2c.I2cController')
def test_init_device_address_error(mock_controller):
    address = 'foo'
    with pytest.raises(luma.core.error.DeviceAddressError) as ex:
        ftdi_i2c(device='ftdi://dummy', address=address)
    assert str(ex.value) == f'I2C device address invalid: {address}'
