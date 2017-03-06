#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.device.dummy` class.
"""

import os.path
from PIL import Image, ImageChops

from luma.core.render import canvas
from luma.core.device import dummy

import baseline_data


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
    reference = Image.open(
        os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            'reference',
            'portrait.png')))

    device = dummy(rotate=1)

    # Use the same drawing primitives as the demo
    with canvas(device) as draw:
        baseline_data.primitives(device, draw)

    bbox = ImageChops.difference(reference, device.image).getbbox()
    assert bbox is None


def test_dither():
    reference = Image.open(
        os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            'reference',
            'dither.png')))

    device = dummy(mode="1")

    with canvas(device, dither=True) as draw:
        draw.rectangle((0, 0, 64, 32), fill="red")
        draw.rectangle((64, 0, 128, 32), fill="yellow")
        draw.rectangle((0, 32, 64, 64), fill="blue")
        draw.rectangle((64, 32, 128, 64), fill="white")

    bbox = ImageChops.difference(reference, device.image).getbbox()
    assert bbox is None
