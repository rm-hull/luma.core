#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.image_composition` class and associated
helpers.
"""

import pytest

from PIL import Image

from luma.core.image_composition import ComposableImage


def test_composable_image_none():
    with pytest.raises(AssertionError):
        ComposableImage(None)


def test_composable_image_attributes():
    pos = (78, 12)
    offs = (90, 12)
    img_size = (123, 234)
    img = Image.new("RGB", img_size)
    ci = ComposableImage(img)
    ci.position = pos
    ci.offset = offs
    ci.image = img
    assert ci.position == pos
    assert ci.offset == offs
    assert ci.width == img_size[0]
    assert ci.height == img_size[1]


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
