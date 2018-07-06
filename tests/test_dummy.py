#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.device.dummy` class.
"""

from PIL import Image

from luma.core.render import canvas
from luma.core.device import dummy

import baseline_data
from helpers import get_reference_image, assert_identical_image


def test_capture_noops():
    device = dummy()
    # All these should have no effect
    device.hide()
    device.show()
    device.cleanup()
    device.contrast(123)
    device.command(1, 2, 4, 4)
    device.data([1, 2, 4, 4])


def test_portrait():
    img_path = get_reference_image('portrait.png')

    with open(img_path, 'rb') as p:
        reference = Image.open(p)

        device = dummy(rotate=1)

        # Use the same drawing primitives as the demo
        with canvas(device) as draw:
            baseline_data.primitives(device, draw)

        assert_identical_image(reference, device.image, img_path)


def test_dither():
    img_path = get_reference_image('dither.png')

    with open(img_path, 'rb') as p:
        reference = Image.open(p)
        device = dummy(mode="1")

        with canvas(device, dither=True) as draw:
            draw.rectangle((0, 0, 64, 32), fill="red")
            draw.rectangle((64, 0, 128, 32), fill="yellow")
            draw.rectangle((0, 32, 64, 64), fill="blue")
            draw.rectangle((64, 32, 128, 64), fill="white")

        assert_identical_image(reference, device.image, img_path)
