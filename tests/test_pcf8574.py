#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.interface.serial.pcf8574` class.
"""

import errno
import pytest

from unittest.mock import Mock, call
from luma.core.interface.serial import pcf8574
import luma.core.error


smbus = Mock(unsafe=True)
BACKLIGHT = 0x08
ENABLE = 0x04
COMMAND = 0x00
DATA = 0x01


def setup_function(function):
    smbus.reset_mock()


def test_command():
    cmds = [3, 1, 4]
    serial = pcf8574(bus=smbus, address=0x27)
    serial.command(*cmds)

    calls = []
    for c in cmds:
        calls += [call(0x27, BACKLIGHT | COMMAND | c << 4)]
        calls += [call(0x27, BACKLIGHT | COMMAND | c << 4 | ENABLE)]
        calls += [call(0x27, BACKLIGHT | COMMAND | c << 4)]

    smbus.write_byte.assert_has_calls(calls)


def test_i2c_command_device_not_found_error():
    errorbus = Mock(unsafe=True)
    address = 0x27
    cmds = [3, 1, 4]
    expected_error = OSError()

    try:
        for error_code in [errno.EREMOTEIO, errno.EIO]:
            expected_error.errno = error_code
            errorbus.write_byte.side_effect = expected_error

            serial = pcf8574(bus=errorbus, address=address)
            with pytest.raises(luma.core.error.DeviceNotFoundError) as ex:
                serial.command(*cmds)

            assert str(ex.value) == 'I2C device not found on address: 0x{0:02X}'.format(
                address)
    except AttributeError as e:
        # osx
        pytest.skip(str(e))


def test_i2c_data():
    data = list((5, 4, 3, 2, 1))
    serial = pcf8574(bus=smbus, address=0x21)
    serial.data(data)

    calls = []
    for d in data:
        calls += [call(0x21, BACKLIGHT | DATA | d << 4)]
        calls += [call(0x21, BACKLIGHT | DATA | d << 4 | ENABLE)]
        calls += [call(0x21, BACKLIGHT | DATA | d << 4)]

    smbus.write_byte.assert_has_calls(calls)


def test_cleanup():
    serial = pcf8574(bus=smbus, address=0x9F)
    serial._managed = True
    serial.cleanup()
    smbus.close.assert_called_once_with()
