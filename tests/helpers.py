# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Test helpers.
"""

import os.path
import platform
import pytest

from PIL import ImageChops, ImageFont


rpi_gpio_missing = 'RPi.GPIO is not supported on this platform: {}'.format(
    platform.system())
spidev_missing = 'spidev is not supported on this platform: {}'.format(
    platform.system())
pyftdi_missing = 'pyftdi is not supported on Python {}'.format(platform.python_version())


def get_reference_file(fname):
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        'reference',
        fname))


def get_reference_image(fname):
    return get_reference_file(os.path.join('images', fname))


def get_reference_font(fname, fsize=12):
    path = get_reference_file(os.path.join('font', fname))
    return ImageFont.truetype(path, fsize)


def get_spidev():
    try:
        import spidev
        return spidev
    except ImportError:
        pytest.skip(spidev_missing)


def assert_identical_image(reference, target, img_path):
    bbox = ImageChops.difference(reference, target).getbbox()
    assert bbox is None, '{0} is not identical to generated image'.format(
        os.path.basename(img_path))


def i2c_error(path_name, err_no):
    expected_error = OSError()
    expected_error.errno = err_no
    expected_error.filename = path_name

    def fake_open(a, b):
        raise expected_error
    return fake_open


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b
