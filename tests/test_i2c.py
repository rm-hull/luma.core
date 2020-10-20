#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-2020 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.interface.serial.i2c` class.
"""

import errno
import pytest
import smbus2
from unittest.mock import Mock, patch, call
from luma.core.interface.serial import i2c
import luma.core.error

from helpers import i2c_error, fib


smbus = Mock(unsafe=True)


def setup_function(function):
    smbus.reset_mock()


def test_init_device_not_found():
    port = 200
    address = 0x710
    path_name = f'/dev/i2c-{port}'
    fake_open = i2c_error(path_name, errno.ENOENT)

    with patch('os.open', fake_open):
        with pytest.raises(luma.core.error.DeviceNotFoundError) as ex:
            i2c(port=port, address=address)
        assert str(ex.value) == f'I2C device not found: {path_name}'


def test_init_device_permission_error():
    port = 1
    path_name = f'/dev/i2c-{port}'
    fake_open = i2c_error(path_name, errno.EACCES)

    with patch('os.open', fake_open):
        try:
            i2c(port=port)
        except luma.core.error.DevicePermissionError as ex:
            # permission error: device exists but no permission
            assert str(ex) == f'I2C device permission denied: {path_name}'


def test_init_device_address_error():
    address = 'foo'
    with pytest.raises(luma.core.error.DeviceAddressError) as ex:
        i2c(address=address)
    assert str(ex.value) == f'I2C device address invalid: {address}'


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

    try:
        for error_code in [errno.EREMOTEIO, errno.EIO]:
            expected_error.errno = error_code
            errorbus.write_i2c_block_data.side_effect = expected_error

            serial = i2c(bus=errorbus, address=address)
            with pytest.raises(luma.core.error.DeviceNotFoundError) as ex:
                serial.command(*cmds)

            assert str(ex.value) == 'I2C device not found on address: 0x{0:02X}'.format(
                address)
    except AttributeError as e:
        # osx
        pytest.skip(str(e))


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
