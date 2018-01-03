#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.image_composition` class and associated
helpers.
"""

import pytest
import PIL

from PIL import Image, ImageDraw
from luma.core.device import dummy
from luma.core.image_composition import ComposableImage, ImageComposition


def test_composable_image_none():
    with pytest.raises(AssertionError):
        ComposableImage(None)


def test_composable_image_image():
    ci = ComposableImage(Image.new("RGB", (1, 1)))
    with pytest.raises(AssertionError):
        ci.image((0, 0))

    with pytest.raises(AssertionError):
        ci.image((1, 0))

    with pytest.raises(AssertionError):
        ci.image((0, 1))


def test_composable_image_ctor():
    pos = (78, 12)
    offs = (90, 12)
    img_size = (123, 234)
    img = Image.new("RGB", img_size)
    ci = ComposableImage(img)
    ci.position = pos
    ci.offset = offs
    assert ci.position == pos
    assert ci.offset == offs
    assert ci.width == img_size[0]
    assert ci.height == img_size[1]
    assert isinstance(ci.image((1, 1)), PIL.Image.Image)


def test_composable_image_crop_same():
    img_size = (128, 64)
    crop_size = img_size
    img = Image.new("RGB", img_size)
    ci = ComposableImage(img)
    cropped_img = ci.image(crop_size)
    assert cropped_img.size == crop_size


def test_composable_image_crop_size_smaller_than_image_size():
    img_size = (128, 64)
    crop_size = (10, 10)
    img = Image.new("RGB", img_size)
    ci = ComposableImage(img)
    cropped_img = ci.image(crop_size)
    assert cropped_img.size == crop_size


def test_composable_image_crop_size_greater_than_image_size():
    img_size = (128, 64)
    crop_size = (1000, 1000)
    img = Image.new("RGB", img_size)
    ci = ComposableImage(img)
    cropped_img = ci.image(crop_size)
    assert cropped_img.size == img_size


def test_composable_image_crop_offset():
    img_size = (128, 64)
    crop_size = (10, 10)
    img = Image.new("RGB", img_size)
    ci = ComposableImage(img, offset=(20, 20))
    cropped_img = ci.image(crop_size)
    assert cropped_img.size == crop_size


def test_image_composition_ctor():
    ic = ImageComposition(dummy())
    assert isinstance(ic(), PIL.Image.Image)


def test_image_add_image_none():
    ic = ImageComposition(dummy())
    with pytest.raises(AssertionError):
        ic.add_image(None)


def test_image_remove_image_none():
    ic = ImageComposition(dummy())
    with pytest.raises(AssertionError):
        ic.remove_image(None)


def test_image_count():
    ic = ImageComposition(dummy())
    img1 = ComposableImage(Image.new("RGB", (1, 1)))
    img2 = ComposableImage(Image.new("RGB", (1, 1)))
    img3 = ComposableImage(Image.new("RGB", (1, 1)))
    ic.add_image(img1)
    ic.add_image(img2)
    ic.add_image(img3)
    assert len(ic.composed_images) == 3
    ic.remove_image(img3)
    assert len(ic.composed_images) == 2
    ic.remove_image(img2)
    assert len(ic.composed_images) == 1
    ic.remove_image(img1)
    assert len(ic.composed_images) == 0


def test_refresh_no_images():
    ic = ImageComposition(dummy())
    ic_img_before = list(ic().getdata())
    ic.refresh()
    assert ic_img_before == list(ic().getdata())


def test_refresh():
    ic = ImageComposition(dummy())
    ic_img_before = list(ic().getdata())
    img = Image.new("RGB", (25, 25))
    draw = ImageDraw.Draw(img)
    draw.rectangle((10, 10, 20, 20), outline="white")
    del draw
    ci = ComposableImage(img)
    ic.add_image(ci)
    ic.refresh()
    assert ic_img_before != list(ic().getdata())
