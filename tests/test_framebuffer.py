#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

from PIL import Image, ImageDraw
from luma.core.device import dummy
from luma.core.framebuffer import full_frame, diff_to_previous


im1 = Image.new("RGB", (40, 40))
draw = ImageDraw.Draw(im1)
draw.line((0, 0) + (39, 39), fill="white")

im2 = Image.new("RGB", (40, 40))
draw = ImageDraw.Draw(im2)
draw.line((0, 0) + (39, 39), fill="white")
draw.line((0, 39) + (39, 0), fill="white")

device = dummy(width=40, height=40, mode="1")


def test_full_frame():
    framebuffer = full_frame()
    redraws = list(framebuffer.redraw(im1))
    assert len(redraws) == 1
    assert redraws[0][0] == im1
    assert redraws[0][1] == im1.getbbox()


def test_diff_to_previous():
    framebuffer = diff_to_previous(device, num_segments=4)
    redraws = list(framebuffer.redraw(im1))

    # First redraw should be the full image
    assert len(redraws) == 1
    assert redraws[0][0] == im1
    assert redraws[0][1] == im1.getbbox()
    assert redraws[0][1] is not None

    # Redraw of same image should return empty changeset
    redraws = list(framebuffer.redraw(im1))
    assert len(redraws) == 0

    # Redraw of new image should return two changesets
    redraws = list(framebuffer.redraw(im2))
    assert len(redraws) == 2

    assert redraws[0][0] == im2.crop((0, 20, 20, 40))
    assert redraws[0][1] == (0, 20, 20, 40)

    assert redraws[1][0] == im2.crop((20, 0, 40, 20))
    assert redraws[1][1] == (20, 0, 40, 20)

    # Redraw of original image should return two changesets
    redraws = list(framebuffer.redraw(im1))
    assert len(redraws) == 2

    assert redraws[0][0] == im1.crop((0, 20, 20, 40))
    assert redraws[0][1] == (0, 20, 20, 40)

    assert redraws[1][0] == im1.crop((20, 0, 40, 20))
    assert redraws[1][1] == (20, 0, 40, 20)
