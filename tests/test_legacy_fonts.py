#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2020 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.legacy.fonts` class.
"""

from PIL import Image
from luma.core.device import dummy
from luma.core.render import canvas
from luma.core.legacy import text, textsize
import luma.core.legacy.font
from luma.core.legacy.font import proportional

import pytest
from helpers import get_reference_image, assert_identical_image


charset = ''.join(chr(i) for i in range(256))


@pytest.mark.parametrize("fontname",
                         ["CP437_FONT", "SINCLAIR_FONT", "LCD_FONT",
                          "UKR_FONT", "TINY_FONT", "SEG7_FONT"])
def test_font(fontname):
    font = getattr(luma.core.legacy.font, fontname)
    w, h = textsize(charset, proportional(font))
    device = dummy(width=w, height=h, mode="1")
    with canvas(device) as draw:
        text(draw, (0, 0), charset, "white", font=proportional(font))

    img_path = get_reference_image(f'{fontname}.png')
    with open(img_path, 'rb') as fp:
        reference = Image.open(fp)
        assert_identical_image(reference, device.image, img_path)
