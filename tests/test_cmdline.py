#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:mod:`luma.core.cmdline` module.
"""

import errno

from luma.core import cmdline, error
from luma.core.interface.serial import __all__ as iface_types

from helpers import (get_reference_file, patch, Mock, i2c_error,
    rpi_gpio_missing, spidev_missing)

import pytest


test_config_file = get_reference_file('config-test.txt')


class test_spi_opts(object):
    spi_port = 0
    spi_device = 0
    spi_bus_speed = 8000000
    gpio_data_command = 24
    gpio_reset = 25
    gpio_backlight = 18

    interface = 'spi'


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


def test_get_library_version():
    """
    :py:func:`luma.core.cmdline.get_library_version` returns the version number
    for the specified library name.
    """
    lib_name = 'hotscreenz'
    lib_version = '0.1.2'

    # set version nr for fake luma library
    luma_fake_lib = Mock()
    luma_fake_lib.__version__ = lib_version

    with patch.dict('sys.modules', {'luma.' + lib_name: luma_fake_lib}):
        assert cmdline.get_library_version(lib_name) == lib_version


def test_get_library_for_display_type():
    """
    :py:func:`luma.core.cmdline.get_library_for_display_type` returns the
    the library name for a particular display.
    """
    display_type = 'coolscreen'
    lib_name = 'screens'

    with patch('luma.core.cmdline.get_display_types') as mocka:
        mocka.return_value = {
            lib_name: [display_type, 'bar'],
            'emulator': ['x', 'y']
        }
        assert cmdline.get_library_for_display_type(display_type) == lib_name


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
    with patch.dict('sys.modules', **{
            'luma.emulator': Mock(),
            'luma.emulator.render': Mock(),
        }):
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
    try:
        factory = cmdline.make_serial(test_spi_opts)
        assert 'luma.core.interface.serial.spi' in repr(factory.spi())
    except ImportError:
        # non-rpi platform, e.g. macos
        pytest.skip(rpi_gpio_missing)
    except error.UnsupportedPlatform as e:
        # non-rpi platform, e.g. ubuntu 64-bit
        pytest.skip('{0} ({1})'.format(type(e).__name__, str(e)))


def test_make_serial_spi_alt_gpio():
    """
    :py:func:`luma.core.cmdline.make_serial.spi` returns an SPI instance
    when using an alternative GPIO implementation.
    """
    class opts(test_spi_opts):
        gpio = 'fake_gpio'

    with patch.dict('sys.modules', **{
            'fake_gpio': Mock(unsafe=True)
        }):
        try:
            factory = cmdline.make_serial(opts)
            assert 'luma.core.interface.serial.spi' in repr(factory.spi())
        except ImportError:
            pytest.skip(spidev_missing)
        except error.DeviceNotFoundError as e:
            # non-rpi platform, e.g. ubuntu 64-bit
            pytest.skip('{0} ({1})'.format(type(e).__name__, str(e)))


def test_create_device():
    """
    :py:func:`luma.core.cmdline.create_device` returns ``None`` for unknown
    displays.
    """
    class args:
        display = 'foo'
    assert cmdline.create_device(args) is None


def test_create_device_oled():
    """
    :py:func:`luma.core.cmdline.create_device` supports OLED displays.
    """
    display_name = 'oled1234'
    display_types = {'oled': [display_name]}

    class args(test_spi_opts):
        display = display_name

    module_mock = Mock()
    module_mock.oled.device.oled1234.return_value = display_name
    with patch.dict('sys.modules', **{
            # mock luma.oled package
            'luma': module_mock,
            'luma.oled': module_mock,
            'luma.oled.device': module_mock
        }):
        try:
            device = cmdline.create_device(args, display_types=display_types)
            assert device == display_name
        except ImportError:
            pytest.skip(rpi_gpio_missing)
        except error.UnsupportedPlatform as e:
            # non-rpi platform
            pytest.skip('{0} ({1})'.format(type(e).__name__, str(e)))


def test_create_device_lcd():
    """
    :py:func:`luma.core.cmdline.create_device` supports LCD displays.
    """
    display_name = 'lcd1234'
    display_types = {'lcd': [display_name], 'oled': []}

    class args(test_spi_opts):
        display = display_name
        gpio = 'fake_gpio'
        backlight_active = 'low'

    module_mock = Mock()
    module_mock.lcd.device.lcd1234.return_value = display_name
    with patch.dict('sys.modules', **{
            # mock spidev and luma.lcd packages
            'fake_gpio': module_mock,
            'spidev': module_mock,
            'luma': module_mock,
            'luma.lcd': module_mock,
            'luma.lcd.aux': module_mock,
            'luma.lcd.device': module_mock
        }):
        device = cmdline.create_device(args, display_types=display_types)
        assert device == display_name


def test_create_device_led_matrix():
    """
    :py:func:`luma.core.cmdline.create_device` supports LED matrix displays.
    """
    display_name = 'matrix1234'
    display_types = {'led_matrix': [display_name], 'lcd': [], 'oled': []}

    class args(test_spi_opts):
        display = display_name

    module_mock = Mock()
    module_mock.led_matrix.device.matrix1234.return_value = display_name
    with patch.dict('sys.modules', **{
            # mock spidev and luma.led_matrix packages
            'spidev': module_mock,
            'luma': module_mock,
            'luma.led_matrix': module_mock,
            'luma.led_matrix.device': module_mock
        }):
        device = cmdline.create_device(args, display_types=display_types)
        assert device == display_name


def test_create_device_emulator():
    """
    :py:func:`luma.core.cmdline.create_device` supports emulators.
    """
    display_name = 'emulator1234'
    display_types = {'emulator': [display_name], 'led_matrix': [], 'lcd': [], 'oled': []}

    class args(test_spi_opts):
        display = display_name

    module_mock = Mock()
    module_mock.emulator.device.emulator1234.return_value = display_name
    with patch.dict('sys.modules', **{
            # mock spidev and luma.emulator packages
            'spidev': module_mock,
            'luma': module_mock,
            'luma.emulator': module_mock,
            'luma.emulator.device': module_mock
        }):
        device = cmdline.create_device(args, display_types=display_types)
        assert device == display_name
