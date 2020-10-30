#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

from PIL import Image, ImageDraw
from luma.core.framebuffer import full_frame, diff_to_previous


im1 = Image.new("RGB", (40, 40))
draw = ImageDraw.Draw(im1)
draw.line((0, 0) + (39, 39), fill="white")

im2 = Image.new("RGB", (40, 40))
draw = ImageDraw.Draw(im2)
draw.line((0, 0) + (39, 39), fill="white")
draw.line((0, 39) + (39, 0), fill="white")


def test_full_frame():
    framebuffer = full_frame()
    redraws = list(framebuffer.redraw(im1))
    assert len(redraws) == 1
    assert redraws[0][0] == im1
    assert redraws[0][1] == im1.getbbox()


def test_diff_to_previous():
    framebuffer = diff_to_previous(num_segments=4)
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
    assert redraws[0][1] == (20, 0, 40, 20)

    assert redraws[1][0] == im2.crop((20, 0, 40, 20))
    assert redraws[1][1] == (0, 20, 20, 40)

    # Redraw of original image should return two changesets
    redraws = list(framebuffer.redraw(im1))
    assert len(redraws) == 2

    assert redraws[0][0] == im1.crop((20, 0, 40, 20))
    assert redraws[0][1] == (20, 0, 40, 20)

    assert redraws[1][0] == im1.crop((0, 20, 20, 40))
    assert redraws[1][1] == (0, 20, 20, 40)


def test_diff_to_previous_debug():
    framebuffer = diff_to_previous(num_segments=4, debug=True)
    redraws = list(framebuffer.redraw(im1))

    # First redraw should be the full image unchanged
    assert len(redraws) == 1
    assert redraws[0][0] == im1

    # Redraw of new image should return two changesets with red borders around them
    redraws = list(framebuffer.redraw(im2))
    assert len(redraws) == 2

    first_changeset_image = im2.copy().crop((20, 0, 40, 20))
    draw = ImageDraw.Draw(first_changeset_image)
    draw.rectangle((0, 0, 19, 19), outline="red")
    del draw
    assert redraws[0][0] == first_changeset_image

    second_changeset_image = im2.copy().crop((0, 20, 20, 40))
    draw = ImageDraw.Draw(second_changeset_image)
    draw.rectangle((0, 0, 19, 19), outline="red")
    del draw
    assert redraws[1][0] == second_changeset_image
