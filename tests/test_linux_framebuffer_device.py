#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.device.framebuffer` class.
"""
import os
import pytest

from luma.core.render import canvas
from luma.core.device import linux_framebuffer
import luma.core.error

from helpers import multi_mock_open, get_reference_file
from unittest.mock import patch, call

SCREEN_RES = "124,55"
BITS_PER_PIXEL = "24"


def test_display_id_as_dev_fb_number():
    with patch("builtins.open", multi_mock_open(SCREEN_RES, BITS_PER_PIXEL)):
        device = linux_framebuffer("/dev/fb9")
        assert device.id == 9


def test_display_id_from_environ():
    os.environ["FRAMEBUFFER"] = "/dev/fb16"
    with patch("builtins.open", multi_mock_open(SCREEN_RES, BITS_PER_PIXEL)):
        device = linux_framebuffer()
        assert device.id == 16


def test_unknown_display_id():
    with patch("builtins.open", multi_mock_open(SCREEN_RES, BITS_PER_PIXEL)):
        with pytest.raises(luma.core.error.DeviceNotFoundError):
            linux_framebuffer("invalid fb")


def test_read_screen_resolution():
    with patch(
        "builtins.open", multi_mock_open(SCREEN_RES, BITS_PER_PIXEL)
    ) as fake_open:
        device = linux_framebuffer("/dev/fb1")
        assert device.width == 124
        assert device.height == 55
        fake_open.assert_has_calls([call("/sys/class/graphics/fb1/virtual_size", "r")])


def test_read_bits_per_pixel():
    with patch(
        "builtins.open", multi_mock_open(SCREEN_RES, BITS_PER_PIXEL)
    ) as fake_open:
        device = linux_framebuffer("/dev/fb1")
        assert device.bits_per_pixel == 24
        fake_open.assert_has_calls(
            [call("/sys/class/graphics/fb1/bits_per_pixel", "r")]
        )


def test_display_16bpp():
    with open(get_reference_file("fb_16bpp.raw"), "rb") as fp:
        reference = fp.read()

    with patch("builtins.open", multi_mock_open(SCREEN_RES, "16", None)) as fake_open:
        device = linux_framebuffer("/dev/fb1")
        with canvas(device, dither=True) as draw:
            draw.rectangle((0, 0, 64, 32), fill="red")
            draw.rectangle((64, 0, 128, 32), fill="yellow")
            draw.rectangle((0, 32, 64, 64), fill="orange")
            draw.rectangle((64, 32, 128, 64), fill="white")

    fake_open.assert_has_calls([call("/dev/fb1", "wb")])
    fake_open.return_value.write.assert_called_once_with(reference)


def test_display_24bpp():
    with open(get_reference_file("fb_24bpp.raw"), "rb") as fp:
        reference = fp.read()

    with patch("builtins.open", multi_mock_open(SCREEN_RES, "24", None)) as fake_open:
        device = linux_framebuffer("/dev/fb1")
        with canvas(device, dither=True) as draw:
            draw.rectangle((0, 0, 64, 32), fill="red")
            draw.rectangle((64, 0, 128, 32), fill="yellow")
            draw.rectangle((0, 32, 64, 64), fill="orange")
            draw.rectangle((64, 32, 128, 64), fill="white")

    fake_open.assert_has_calls([call("/dev/fb1", "wb")])
    fake_open.return_value.write.assert_called_once_with(reference)


def test_unsupported_bit_depth():

    with patch("builtins.open", multi_mock_open(SCREEN_RES, "32", None)):
        with pytest.raises(AssertionError) as ex:
            linux_framebuffer("/dev/fb4")
        assert str(ex.value) == 'Unsupported bit-depth: 32'
