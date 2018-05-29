#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.render.canvas` class.
"""

import pytest

from PIL import Image

from luma.core.device import dummy
from luma.core.render import canvas

from helpers import get_reference_image, assert_identical_image


def test_canvas_background():
    img_path = get_reference_image('background.png')
    with open(get_reference_image('dither.png'), 'rb') as p1:
        with open(img_path, 'rb') as p2:
            bgnd = Image.open(p1)
            reference = Image.open(p2)
            device = dummy()

            with canvas(device, background=bgnd) as draw:
                draw.rectangle((20, 15, device.width - 20, device.height - 15),
                               fill='black', outline='white')
                draw.text((36, 22), 'Background', fill='white')
                draw.text((52, 32), 'Test', fill='white')

            assert_identical_image(reference, device.image, img_path)


def test_canvas_wrong_size():
    with pytest.raises(AssertionError):
        canvas(dummy(), background=Image.new('RGB', (23, 97)))
