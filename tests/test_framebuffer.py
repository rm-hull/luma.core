#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

from PIL import Image, ImageDraw
from luma.core.device import dummy
from luma.core.framebuffer import full_frame, diff_to_previous


im1 = Image.new("1", (4, 4))
draw = ImageDraw.Draw(im1)
draw.line((0, 0) + (3, 0), fill="white")

im2 = Image.new("1", (4, 4))
draw = ImageDraw.Draw(im2)
draw.line((0, 0) + (3, 0), fill="white")
draw.line((0, 0) + (0, 3), fill="white")

device = dummy(width=4, height=4, mode="1")


def test_full_frame():
    framebuffer = full_frame(device)
    assert framebuffer.redraw_required(im1)
    pix1 = list(framebuffer.getdata())
    assert len(pix1) == 16
    assert pix1 == [0xFF] * 4 + [0x00] * 12
    assert framebuffer.bounding_box == (0, 0, 4, 4)
    assert framebuffer.inflate_bbox() == (0, 0, 4, 4)

    assert framebuffer.redraw_required(im2)
    pix2 = list(framebuffer.getdata())
    assert len(pix2) == 16
    assert pix2 == [0xFF] * 4 + [0xFF, 0x00, 0x00, 0x00] * 3
    assert framebuffer.bounding_box == (0, 0, 4, 4)

    assert framebuffer.redraw_required(im2)
    pix3 = list(framebuffer.getdata())
    assert len(pix3) == 16
    assert pix3 == [0xFF] * 4 + [0xFF, 0x00, 0x00, 0x00] * 3
    assert framebuffer.bounding_box == (0, 0, 4, 4)


def test_diff_to_previous():
    framebuffer = diff_to_previous(device)
    assert framebuffer.redraw_required(im1)
    pix1 = list(framebuffer.getdata())
    assert len(pix1) == 12
    assert pix1 == [0x00] * 12
    assert framebuffer.bounding_box == (0, 1, 4, 4)
    assert framebuffer.inflate_bbox() == (0, 1, 4, 4)

    assert framebuffer.redraw_required(im2)
    pix2 = list(framebuffer.getdata())
    assert len(pix2) == 3
    assert pix2 == [0xFF] * 3
    assert framebuffer.bounding_box == (0, 1, 1, 4)
    assert framebuffer.inflate_bbox() == (0, 1, 4, 4)

    assert not framebuffer.redraw_required(im2)
    assert framebuffer.getdata() is None
    assert framebuffer.bounding_box is None
