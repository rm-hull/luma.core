#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.serial.i2c` class.
"""

import errno
import pytest
import smbus2
from luma.core.serial import i2c
import luma.core.error

from pyfakefs import fake_filesystem

from helpers import Mock, patch, call


smbus = Mock(unsafe=True)


def setup_function(function):
    smbus.reset_mock()


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


class FakeI2COsModule(fake_filesystem.FakeOsModule):
    def open(self, file_path, flags, mode=None):
        try:
            super(FakeI2COsModule, self).open(file_path, flags, mode)
        except NotImplementedError:
            raise self.expected_error


def test_init_device_not_found(fs):
    port = 200
    address = 0x710
    path_name = '/dev/i2c-{}'.format(port)
    os_module = FakeI2COsModule(fs)
    os_module.expected_error = OSError()
    os_module.expected_error.errno = errno.ENOENT
    os_module.expected_error.filename = path_name

    with patch('smbus2.smbus2.os', os_module):
        with pytest.raises(luma.core.error.DeviceNotFoundError) as ex:
            i2c(port=port, address=address)
        assert str(ex.value) == 'I2C device not found: {}'.format(path_name)


def test_init_device_permission_error(fs):
    port = 1
    path_name = '/dev/i2c-{}'.format(port)
    os_module = FakeI2COsModule(fs)
    os_module.expected_error = OSError()
    os_module.expected_error.errno = errno.EACCES
    os_module.expected_error.filename = path_name

    with patch('smbus2.smbus2.os', os_module):
        try:
            i2c(port=port)
        except luma.core.error.DevicePermissionError as ex:
            # permission error: device exists but no permission
            assert str(ex) == 'I2C device permission denied: {}'.format(
                path_name)


def test_init_device_address_error():
    address = 'foo'
    with pytest.raises(luma.core.error.DeviceAddressError) as ex:
        i2c(address=address)
    assert str(ex.value) == 'I2C device address invalid: {}'.format(address)


def test_init_no_bus():
    with patch.object(smbus2.SMBus, 'open') as mock:
        i2c(port=2, address=0x71)
    mock.assert_called_once_with(2)


def test_init_bus_provided():
    i2c(bus=smbus, address=0x71)
    smbus.open.assert_not_called()


def test_command():
    cmds = [3, 1, 4, 2]
    serial = i2c(bus=smbus, address=0x83)
    serial.command(*cmds)
    smbus.write_i2c_block_data.assert_called_once_with(0x83, 0x00, cmds)


def test_i2c_command_device_not_found_error():
    errorbus = Mock(unsafe=True)
    address = 0x71
    cmds = [3, 1, 4, 2]
    expected_error = OSError()

    for error_code in [errno.EREMOTEIO, errno.EIO]:
        expected_error.errno = error_code
        errorbus.write_i2c_block_data.side_effect = expected_error

        serial = i2c(bus=errorbus, address=address)
        with pytest.raises(luma.core.error.DeviceNotFoundError) as ex:
            serial.command(*cmds)

        assert str(ex.value) == 'I2C device not found on address: {}'.format(
            address)


def test_i2c_data():
    data = list(fib(10))
    serial = i2c(bus=smbus, address=0x21)
    serial.data(data)
    smbus.write_i2c_block_data.assert_called_once_with(0x21, 0x40, data)


def test_i2c_data_chunked():
    data = list(fib(100))
    serial = i2c(bus=smbus, address=0x66)
    serial.data(data)
    calls = [call(0x66, 0x40, data[i:i + 32]) for i in range(0, 100, 32)]
    smbus.write_i2c_block_data.assert_has_calls(calls)


def test_cleanup():
    serial = i2c(bus=smbus, address=0x9F)
    serial._managed = True
    serial.cleanup()
    smbus.close.assert_called_once_with()
