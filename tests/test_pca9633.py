#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-25 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.interface.serial.pca9633` class.
"""

from unittest.mock import Mock, call, ANY
from luma.core.interface.serial import pca9633
import luma.core.error

import pytest

REG_MODE1 = 0x00
REG_MODE2 = 0x01
REG_LEDOUT = 0x08

REG_RED_PWM = 0x04    # PWM2
REG_GREEN_PWM = 0x03  # PWM1
REG_BLUE_PWM = 0x02   # PWM0
REG_GRP_PWM = 0x06    # GRPPWM

smbus = Mock(unsafe=True)   

def setup_function():
    smbus.reset_mock()


def test_init():
    controller = pca9633(bus=smbus)

    calls = [call(i2c_addr = ANY, register = REG_MODE1, value = ANY)] + \
        [call(i2c_addr = ANY, register = REG_MODE2, value = ANY)] + \
        [call(i2c_addr = ANY, register = REG_LEDOUT, value = ANY)]  # Do not enforce any settings

    smbus.write_byte_data.assert_has_calls(calls)


def test_enable_backlight():
    controller = pca9633(bus=smbus)
    controller(True)

    calls = [call(i2c_addr = ANY, register = REG_RED_PWM, value = 255)] + \
        [call(i2c_addr = ANY, register = REG_GREEN_PWM, value = 255)] + \
        [call(i2c_addr = ANY, register = REG_BLUE_PWM, value = 255)]

    smbus.write_byte_data.assert_has_calls(calls)


def test_set_brightness():
    controller = pca9633(bus=smbus)
    controller(True)
    controller.set_brightness(128)

    calls = [call(i2c_addr = ANY, register = REG_GRP_PWM, value = 128)]

    smbus.write_byte_data.assert_has_calls(calls)


def test_set_color():
    controller = pca9633(bus=smbus)
    controller(True)
    controller.set_color(0,64,128)

    calls = [call(i2c_addr = ANY, register = REG_RED_PWM, value = 0)] + \
        [call(i2c_addr = ANY, register = REG_GREEN_PWM, value = 64)] + \
        [call(i2c_addr = ANY, register = REG_BLUE_PWM, value = 128)]

    smbus.write_byte_data.assert_has_calls(calls)


def test_set_brightness_with_backlight_disabled():
    controller = pca9633(bus=smbus)
    controller(False)
    controller.set_brightness(128)

    calls = call(i2c_addr = ANY, register = REG_GRP_PWM, value = 128)

    assert calls not in smbus.write_byte_data.mock_calls


def test_set_color_with_backlight_disabled():
    controller = pca9633(bus=smbus)
    controller(False)
    controller.set_color(1,64,128)

    calls = [call(i2c_addr = ANY, register = REG_RED_PWM, value = 1)] + \
        [call(i2c_addr = ANY, register = REG_GREEN_PWM, value = 64)] + \
        [call(i2c_addr = ANY, register = REG_BLUE_PWM, value = 128)]

    for c in calls:
        assert c not in smbus.write_byte_data.mock_calls


def test_cleanup():
    controller = pca9633(bus=smbus)
    controller._managed = True
    controller.cleanup()
    smbus.close.assert_called_once()