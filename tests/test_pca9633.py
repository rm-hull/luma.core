#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-25 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.interface.serial.pca9633` class.
"""

from unittest.mock import Mock, call, ANY
from luma.core.interface.serial import pca9633
from luma.core.util import perf_counter

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
    pca9633(bus=smbus)

    calls = [call(i2c_addr=ANY, register=REG_MODE1, value=ANY)] + \
        [call(i2c_addr=ANY, register=REG_MODE2, value=ANY)] + \
        [call(i2c_addr=ANY, register=REG_LEDOUT, value=ANY)]  # Do not enforce any settings

    smbus.write_byte_data.assert_has_calls(calls)


def test_enable_backlight():
    backlight = pca9633(bus=smbus)
    backlight(True)

    calls = [call(i2c_addr=ANY, register=REG_RED_PWM, value=255)] + \
        [call(i2c_addr=ANY, register=REG_GREEN_PWM, value=255)] + \
        [call(i2c_addr=ANY, register=REG_BLUE_PWM, value=255)]

    smbus.write_byte_data.assert_has_calls(calls)


def test_set_brightness():
    backlight = pca9633(bus=smbus)
    backlight(True)
    backlight.set_brightness(128)

    calls = [call(i2c_addr=ANY, register=REG_GRP_PWM, value=128)]

    smbus.write_byte_data.assert_has_calls(calls)


def test_set_color():
    backlight = pca9633(bus=smbus)
    backlight(True)
    backlight.set_color(0, 64, 128)

    calls = [call(i2c_addr=ANY, register=REG_RED_PWM, value=0)] + \
        [call(i2c_addr=ANY, register=REG_GREEN_PWM, value=64)] + \
        [call(i2c_addr=ANY, register=REG_BLUE_PWM, value=128)]

    smbus.write_byte_data.assert_has_calls(calls)


def test_set_brightness_with_backlight_disabled():
    backlight = pca9633(bus=smbus)
    backlight(False)
    backlight.set_brightness(128)

    calls = [call(i2c_addr=ANY, register=REG_GRP_PWM, value=128)]

    assert calls not in smbus.write_byte_data.mock_calls


def test_set_color_with_backlight_disabled():
    backlight = pca9633(bus=smbus)
    backlight(False)
    backlight.set_color(1, 64, 128)

    calls = [call(i2c_addr=ANY, register=REG_RED_PWM, value=1)] + \
        [call(i2c_addr=ANY, register=REG_GREEN_PWM, value=64)] + \
        [call(i2c_addr=ANY, register=REG_BLUE_PWM, value=128)]

    for c in calls:
        assert c not in smbus.write_byte_data.mock_calls


def test_brightness_restored_when_enabled():
    backlight = pca9633(bus=smbus)
    backlight(False)
    backlight.set_brightness(128)
    backlight(True)

    calls = [call(i2c_addr=ANY, register=REG_GRP_PWM, value=128)]

    smbus.write_byte_data.assert_has_calls(calls)


def test_color_restored_when_enabled():
    backlight = pca9633(bus=smbus)
    backlight(False)
    backlight.set_color(1, 64, 128)
    backlight(True)

    calls = [call(i2c_addr=ANY, register=REG_RED_PWM, value=1)] + \
        [call(i2c_addr=ANY, register=REG_GREEN_PWM, value=64)] + \
        [call(i2c_addr=ANY, register=REG_BLUE_PWM, value=128)]

    smbus.write_byte_data.assert_has_calls(calls)


def test_color_gradual():
    backlight = pca9633(bus=smbus)
    backlight(True)
    backlight.set_color(255, 255, 255)
    backlight.set_color(250, 250, 250, duration=1, wait=True)

    calls = [call(i2c_addr=ANY, register=REG_RED_PWM, value=254)] + \
        [call(i2c_addr=ANY, register=REG_GREEN_PWM, value=254)] + \
        [call(i2c_addr=ANY, register=REG_BLUE_PWM, value=254)] + \
        [call(i2c_addr=ANY, register=REG_RED_PWM, value=253)] + \
        [call(i2c_addr=ANY, register=REG_GREEN_PWM, value=253)] + \
        [call(i2c_addr=ANY, register=REG_BLUE_PWM, value=253)] + \
        [call(i2c_addr=ANY, register=REG_RED_PWM, value=252)] + \
        [call(i2c_addr=ANY, register=REG_GREEN_PWM, value=252)] + \
        [call(i2c_addr=ANY, register=REG_BLUE_PWM, value=252)] + \
        [call(i2c_addr=ANY, register=REG_RED_PWM, value=251)] + \
        [call(i2c_addr=ANY, register=REG_GREEN_PWM, value=251)] + \
        [call(i2c_addr=ANY, register=REG_BLUE_PWM, value=251)] + \
        [call(i2c_addr=ANY, register=REG_RED_PWM, value=250)] + \
        [call(i2c_addr=ANY, register=REG_GREEN_PWM, value=250)] + \
        [call(i2c_addr=ANY, register=REG_BLUE_PWM, value=250)]

    smbus.write_byte_data.assert_has_calls(calls)


def test_color_gradual_duration():
    backlight = pca9633(bus=smbus)
    backlight(True)
    before = perf_counter()
    backlight.set_color(250, 250, 250, duration=1, wait=True)
    after = perf_counter()

    duration = after - before

    assert .9 <= duration <= 1.1


def test_cleanup():
    backlight = pca9633(bus=smbus)
    backlight._managed = True
    backlight.cleanup()
    smbus.close.assert_called_once()
