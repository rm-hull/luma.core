#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.


import sys
from unittest.mock import Mock

import pytest

import luma.core.error
from luma.core.lib import spidev, rpi_gpio


@rpi_gpio
class RpiGpioTest(object):
    pass


@spidev
class SpiDevTest(object):
    pass


@spidev
@rpi_gpio
class MultiLibTest(object):
    pass


def assertMethod(obj, method):
    assert hasattr(obj, method)
    assert callable(getattr(obj, method))


def test_rpio_gpio():
    t = RpiGpioTest()
    assertMethod(t, '__rpi_gpio__')


def test_spidev():
    t = SpiDevTest()
    assertMethod(t, '__spidev__')


def test_multi():
    t = MultiLibTest()
    for method in ['__spidev__', '__rpi_gpio__']:
        assertMethod(t, method)


def test_rpi_gpio_unrecognized_runtime_error(monkeypatch):
    fake_gpio = Mock(unsafe=True)
    fake_gpio.setmode.side_effect = RuntimeError('some other platform-specific message')
    fake_rpi = Mock(GPIO=fake_gpio)
    monkeypatch.setitem(sys.modules, 'RPi', fake_rpi)
    monkeypatch.setitem(sys.modules, 'RPi.GPIO', fake_gpio)

    t = RpiGpioTest()
    with pytest.raises(luma.core.error.UnsupportedPlatform):
        t.__rpi_gpio__()
