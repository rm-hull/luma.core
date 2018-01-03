#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.


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
