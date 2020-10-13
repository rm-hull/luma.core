#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Richard Hull and contributors
# See LICENSE.rst for details.

from pathlib import Path

from PIL import Image, ImageFont
from luma.core.device import dummy
from luma.core.virtual import character

from helpers import get_reference_file, get_reference_image, assert_identical_image


def test_init():
    path = get_reference_file(Path('font').joinpath('hd44780a02.pil'))
    fnt = ImageFont.load(path)
    device = dummy(width=80, height=16, mode="1")
    character(device, font=fnt)
    assert device.image == Image.new("1", (80, 16))


def test_setter_getter():
    fnt_path = get_reference_file(Path('font').joinpath('hd44780a02.pil'))
    img_path = get_reference_image('character_golden_ratio.png')

    with open(img_path, 'rb') as img:
        fnt = ImageFont.load(fnt_path)
        reference = Image.open(img)
        device = dummy(width=80, height=16, mode="1")
        c = character(device, font=fnt)
        c.text = "1.61803398875\n1.61803398875"
        assert str(c.text) == "1.61803398875\n1.61803398875"

        assert_identical_image(reference, device.image, img_path)
