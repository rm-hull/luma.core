#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.interface.serial.ftdi_i2c` class.
"""

import pytest
import sys
from luma.core.interface.serial import ftdi_i2c
from helpers import Mock, patch, pyftdi_missing, fib
import luma.core.error


@pytest.mark.skipif(sys.version_info < (3, 5), reason=pyftdi_missing)
@patch('pyftdi.i2c.I2cController')
def test_init(mock_controller):
    instance = Mock()
    instance.get_port = Mock()
    mock_controller.side_effect = [instance]

    ftdi_i2c(device='ftdi://dummy', address='0xFF')
    mock_controller.assert_called_with()
    instance.configure.assert_called_with('ftdi://dummy')
    instance.get_port.assert_called_with(0xFF)


@pytest.mark.skipif(sys.version_info < (3, 5), reason=pyftdi_missing)
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


@pytest.mark.skipif(sys.version_info < (3, 5), reason=pyftdi_missing)
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


@pytest.mark.skipif(sys.version_info < (3, 5), reason=pyftdi_missing)
@patch('pyftdi.i2c.I2cController')
def test_cleanup(mock_controller):
    port = Mock()
    instance = Mock()
    instance.get_port = Mock(return_value=port)
    mock_controller.side_effect = [instance]

    serial = ftdi_i2c(device='ftdi://dummy', address=0x3C)
    serial.cleanup()
    instance.terminate.assert_called_once_with()


@pytest.mark.skipif(sys.version_info < (3, 5), reason=pyftdi_missing)
@patch('pyftdi.i2c.I2cController')
def test_init_device_address_error(mock_controller):
    address = 'foo'
    with pytest.raises(luma.core.error.DeviceAddressError) as ex:
        ftdi_i2c(device='ftdi://dummy', address=address)
    assert str(ex.value) == 'I2C device address invalid: {}'.format(address)
