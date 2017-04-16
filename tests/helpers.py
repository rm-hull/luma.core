# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Test helpers.
"""

import os.path
import platform

try:
    from unittest.mock import patch, call, Mock
except ImportError:
    from mock import patch, call, Mock  # noqa: F401

import pytest


rpi_gpio_missing = 'RPi.GPIO is not supported on this platform: {}'.format(
    platform.system())


def get_reference_file(fname):
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        'reference',
        fname))


def get_reference_image(fname):
    return get_reference_file(os.path.join('images', fname))


def get_spidev():
    try:
        import spidev
        return spidev
    except ImportError:
        pytest.skip('spidev is not supported on this platform: {}'.format(
            platform.system()))
