#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:mod:`luma.core.cmdline` module.
"""

import sys
import errno

from luma.core import cmdline, error
from luma.core.interface.serial import __all__ as iface_types

from helpers import get_reference_file, patch, Mock, i2c_error

import pytest


test_config_file = get_reference_file('config-test.txt')


def test_get_interface_types():
    """
    Enumerate interface types.
    """
    assert cmdline.get_interface_types() == iface_types


def test_get_display_types():
    """
    Enumerate display types.
    """
    assert list(cmdline.get_display_types().keys()) == \
        cmdline.get_supported_libraries()


def test_get_choices_unknown_module():
    """
    :py:func:`luma.core.cmdline.get_choices` returns an empty list when
    trying to inspect an unknown module.
    """
    result = cmdline.get_choices('foo')
    assert result == []


def test_load_config_file_parse():
    """
    :py:func:`luma.core.cmdline.load_config` parses a text file and returns a
    list of arguments.
    """
    result = cmdline.load_config(test_config_file)
    assert result == [
        '--display=capture',
        '--width=800',
        '--height=8600',
        '--spi-bus-speed=16000000'
    ]


def test_create_parser():
    """
    :py:func:`luma.core.cmdline.create_parser` returns an argument parser
    instance.
    """
    sys.modules['luma.emulator'] = Mock()
    sys.modules['luma.emulator.render'] = Mock()

    with patch('luma.core.cmdline.get_display_types') as mocka:
        mocka.return_value = {
            'foo': ['a', 'b'],
            'bar': ['c', 'd'],
            'emulator': ['e', 'f']
        }
        parser = cmdline.create_parser(description='test')
        args = parser.parse_args(['-f', test_config_file])
        assert args.config == test_config_file


def test_make_serial_i2c():
    """
    :py:func:`luma.core.cmdline.make_serial.i2c` returns an I2C instance.
    """
    class opts:
        i2c_port = 200
        i2c_address = 0x710

    path_name = '/dev/i2c-{}'.format(opts.i2c_port)
    fake_open = i2c_error(path_name, errno.ENOENT)
    factory = cmdline.make_serial(opts)

    with patch('os.open', fake_open):
        with pytest.raises(error.DeviceNotFoundError):
            factory.i2c()


def test_make_serial_spi():
    """
    :py:func:`luma.core.cmdline.make_serial.spi` returns an SPI instance.
    """
    class opts:
        spi_port = 0
        spi_device = 0
        spi_bus_speed = 8000000
        gpio_data_command = 24
        gpio_reset = 25
        gpio_backlight = 18

    factory = cmdline.make_serial(opts)
    with pytest.raises(error.UnsupportedPlatform):
        factory.spi()


def test_make_serial_spi_alt_gpio():
    """
    :py:func:`luma.core.cmdline.make_serial.spi` returns an SPI instance
    when using an alternative GPIO implementation.
    """
    class opts:
        spi_port = 0
        spi_device = 0
        spi_bus_speed = 8000000
        gpio_data_command = 24
        gpio_reset = 25
        gpio_backlight = 18
        gpio = 'fake_gpio'

    gpio = Mock(unsafe=True)
    sys.modules['fake_gpio'] = gpio
    factory = cmdline.make_serial(opts)
    with pytest.raises(error.DeviceNotFoundError):
        factory.spi()


def test_create_device():
    """
    :py:func:`luma.core.cmdline.create_device` returns ``None`` for unknown
    displays.
    """
    class args:
        display = 'foo'
    assert cmdline.create_device(args) is None
