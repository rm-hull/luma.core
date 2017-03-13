#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:mod:`luma.core.serial` module.
"""

import errno

try:
    from unittest.mock import patch, call, Mock
except ImportError:
    from mock import patch, call, Mock

import pytest
import smbus2
from luma.core.serial import i2c, spi
import luma.core.error

smbus = Mock(unsafe=True)
spidev = Mock(unsafe=True)
gpio = Mock(unsafe=True)


def setup_function(function):
    smbus.reset_mock()
    spidev.reset_mock()
    gpio.reset_mock()
    gpio.BCM = 1
    gpio.RST = 2
    gpio.DC = 3
    gpio.OUT = 4
    gpio.HIGH = 5
    gpio.LOW = 6


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


# I2C

def test_i2c_init_device_not_found():
    port = 200
    address = 0x710
    with pytest.raises(luma.core.error.DeviceNotFoundError) as ex:
        i2c(port=port, address=address)
    assert str(ex.value) == 'I2C device not found: /dev/i2c-{}'.format(port)


def test_i2c_init_device_permission_error():
    port = 1
    try:
        i2c(port=port)

    except luma.core.error.DevicePermissionError as ex:
        # permission error: device exists but no permission
        assert str(ex) == 'I2C device permission denied: /dev/i2c-{}'.format(
            port)


def test_i2c_init_device_address_error():
    address = 'foo'
    with pytest.raises(luma.core.error.DeviceAddressError) as ex:
        i2c(address=address)
    assert str(ex.value) == 'I2C device address invalid: {}'.format(address)


def test_i2c_init_no_bus():
    with patch.object(smbus2.SMBus, 'open') as mock:
        i2c(port=2, address=0x71)
    mock.assert_called_once_with(2)


def test_i2c_init_bus_provided():
    i2c(bus=smbus, address=0x71)
    smbus.open.assert_not_called()


def test_i2c_command():
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


def test_i2c_cleanup():
    serial = i2c(bus=smbus, address=0x9F)
    serial.cleanup()
    smbus.close.assert_called_once_with()


# SPI

def verify_spi_init(port, device, bus_speed_hz=8000000, dc=24, rst=25):
    spidev.open.assert_called_once_with(port, device)
    assert spidev.max_speed_hz == bus_speed_hz
    gpio.setmode.assert_called_once_with(gpio.BCM)
    gpio.setup.assert_has_calls([call(dc, gpio.OUT), call(rst, gpio.OUT)])


def test_spi_init():
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


def test_spi_init_params_deprecated():
    port = 5
    device = 2
    bus_speed = 16000000
    dc = 80
    rst = 90
    msg1 = 'bcm_DC argument is deprecated in favor of gpio_DC and will be removed in 1.0.0'
    msg2 = 'bcm_RST argument is deprecated in favor of gpio_RST and will be removed in 1.0.0'

    with pytest.deprecated_call() as c:
        spi(gpio=gpio, spi=spidev, port=port, device=device,
            bus_speed_hz=bus_speed, bcm_DC=dc, bcm_RST=rst)
        verify_spi_init(port, device, bus_speed, dc, rst)
        gpio.output.assert_has_calls([
            call(rst, gpio.LOW),
            call(rst, gpio.HIGH)
        ])
        assert str(c.list[0].message) == msg1
        assert str(c.list[1].message) == msg2


def test_spi_init_invalid_bus_speed():
    with pytest.raises(AssertionError):
        spi(gpio=gpio, spi=spidev, port=5, device=2, bus_speed_hz=942312)


def test_spi_command():
    cmds = [3, 1, 4, 2]
    serial = spi(gpio=gpio, spi=spidev, port=9, device=1)
    serial.command(*cmds)
    verify_spi_init(9, 1)
    gpio.output.assert_has_calls([call(25, gpio.HIGH), call(24, gpio.LOW)])
    spidev.writebytes.assert_called_once_with(cmds)


def test_spi_data():
    data = list(fib(100))
    serial = spi(gpio=gpio, spi=spidev, port=9, device=1)
    serial.data(data)
    verify_spi_init(9, 1)
    gpio.output.assert_has_calls([call(25, gpio.HIGH), call(24, gpio.HIGH)])
    spidev.writebytes.assert_called_once_with(data)


def test_spi_cleanup():
    serial = spi(gpio=gpio, spi=spidev, port=9, device=1)
    serial.cleanup()
    verify_spi_init(9, 1)
    spidev.close.assert_called_once_with()
    gpio.cleanup.assert_called_once_with()


def test_spi_init_device_not_found():
    import spidev
    port = 1234
    with pytest.raises(luma.core.error.DeviceNotFoundError) as ex:
        spi(gpio=gpio, spi=spidev.SpiDev(), port=port)
    assert str(ex.value) == 'SPI device not found'


def test_spi_unsupported_gpio_platform():
    try:
        spi(spi=spidev, port=9, device=1)
    except luma.core.error.UnsupportedPlatform as ex:
        assert str(ex) == 'GPIO access not available'
