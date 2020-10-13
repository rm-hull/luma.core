# -*- coding: utf-8 -*-
# Copyright (c) 2017-2020 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Test helpers.
"""

import platform
from pathlib import Path

import pytest
from PIL import ImageChops, ImageFont


rpi_gpio_missing = 'RPi.GPIO is not supported on this platform: {}'.format(
    platform.system())
spidev_missing = 'spidev is not supported on this platform: {}'.format(
    platform.system())


def get_reference_file(fname):
    """
    :param fname: Filename.
    :type fname: str
    """
    return Path(__file__).resolve().parent.joinpath('reference', fname)


def get_reference_image(fname):
    """
    :param fname: Filename.
    :type fname: str
    """
    return get_reference_file(Path('images').joinpath(fname))


def get_reference_font(fname, fsize=12):
    """
    :param fname: Filename of the font.
    :type fname: str
    """
    path = get_reference_file(Path('font').joinpath(fname))
    return ImageFont.truetype(path, fsize)


def get_reference_pillow_font(fname):
    """
    Load PIL.ImageFont type font from provided fname

    :param fname: The name of the file that contains the PIL.ImageFont
    :type fname: str
    :returns `PIL.ImageFont` object
    """
    path = get_reference_file(Path('font').joinpath(fname))
    return ImageFont.load(path)


def get_spidev():
    try:
        import spidev
        return spidev
    except ImportError:
        pytest.skip(spidev_missing)


def assert_identical_image(reference, target, img_path):
    bbox = ImageChops.difference(reference, target).getbbox()
    assert bbox is None, '{0} is not identical to generated image'.format(
        img_path.name)


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
