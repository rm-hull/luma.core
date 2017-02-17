#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

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
