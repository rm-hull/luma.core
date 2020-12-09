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
from luma.core.framebuffer import full_frame
from luma.core.device import linux_framebuffer
import luma.core.error

from helpers import multi_mock_open, get_reference_file
from unittest.mock import patch, call

WIDTH = 124
HEIGHT = 55
SCREEN_RES = f"{WIDTH},{HEIGHT}"
BITS_PER_PIXEL = "24"


def swap_red_and_blue(data, step):
    arr = bytearray(data)
    for i in range(0, len(arr), step):
        [red, green, blue] = arr[i: i + 3]
        arr[i: i + 3] = [blue, green, red]
    return bytes(arr)


def test_display_id_as_dev_fb_number():
    with patch("builtins.open", multi_mock_open(SCREEN_RES, BITS_PER_PIXEL, None)):
        device = linux_framebuffer("/dev/fb9")
        assert device.id == 9


def test_display_id_from_environ():
    os.environ["FRAMEBUFFER"] = "/dev/fb16"
    with patch("builtins.open", multi_mock_open(SCREEN_RES, BITS_PER_PIXEL, None)):
        device = linux_framebuffer()
        assert device.id == 16


def test_unknown_display_id():
    with patch("builtins.open", multi_mock_open(SCREEN_RES, BITS_PER_PIXEL, None)):
        with pytest.raises(luma.core.error.DeviceNotFoundError):
            linux_framebuffer("invalid fb")


def test_read_screen_resolution():
    with patch(
        "builtins.open", multi_mock_open(SCREEN_RES, BITS_PER_PIXEL, None)
    ) as fake_open:
        device = linux_framebuffer("/dev/fb1")
        assert device.width == 124
        assert device.height == 55
        fake_open.assert_has_calls([call("/sys/class/graphics/fb1/virtual_size", "r")])


def test_read_bits_per_pixel():
    with patch(
        "builtins.open", multi_mock_open(SCREEN_RES, BITS_PER_PIXEL, None)
    ) as fake_open:
        device = linux_framebuffer("/dev/fb1")
        assert device.bits_per_pixel == 24
        fake_open.assert_has_calls(
            [call("/sys/class/graphics/fb1/bits_per_pixel", "r")]
        )


@pytest.mark.parametrize("bits_per_pixel,bgr", [
    (16, False),
    (24, False),
    (24, True),
    (32, False),
    (32, True),
])
def test_display(bits_per_pixel, bgr):
    bytes_per_pixel = bits_per_pixel // 8
    with open(get_reference_file(f"fb_{bits_per_pixel}bpp.raw"), "rb") as fp:
        reference = fp.read()
        if bgr:
            reference = swap_red_and_blue(reference, step=bytes_per_pixel)

    with patch("builtins.open", multi_mock_open(SCREEN_RES, str(bits_per_pixel), None)) as fake_open:
        device = linux_framebuffer("/dev/fb1", framebuffer=full_frame(), bgr=bgr)

        fake_open.assert_has_calls([call("/dev/fb1", "wb")])
        fake_open.reset_mock()

        with canvas(device, dither=True) as draw:
            draw.rectangle((0, 0, 64, 32), fill="red")
            draw.rectangle((64, 0, 128, 32), fill="yellow")
            draw.rectangle((0, 32, 64, 64), fill="orange")
            draw.rectangle((64, 32, 128, 64), fill="white")

        fake_open.return_value.seek.assert_has_calls([
            call(n * WIDTH * bytes_per_pixel)
            for n in range(HEIGHT)
        ])
        fake_open.return_value.write.assert_has_calls([
            call(reference[n:n + (WIDTH * bytes_per_pixel)])
            for n in range(0, len(reference), WIDTH * bytes_per_pixel)
        ])
        fake_open.return_value.flush.assert_called_once()


def test_unsupported_bit_depth():
    with patch("builtins.open", multi_mock_open(SCREEN_RES, "19", None)):
        with pytest.raises(AssertionError) as ex:
            linux_framebuffer("/dev/fb4")
        assert str(ex.value) == 'Unsupported bit-depth: 19'


def test_cleanup():
    with patch("builtins.open", multi_mock_open(SCREEN_RES, BITS_PER_PIXEL, None)) as fake_open:
        device = linux_framebuffer("/dev/fb1", framebuffer=full_frame())
        device.cleanup()
        fake_open.return_value.close.assert_called_once()
