#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.virtual.viewport` class and associated
helpers.
"""

import time

from PIL import Image

from luma.core.device import dummy
from luma.core.render import canvas
from luma.core.virtual import range_overlap, hotspot, snapshot, viewport

import baseline_data
from helpers import get_reference_image, assert_identical_image


def overlap(box1, box2):
    l1, t1, r1, b1 = box1
    l2, t2, r2, b2 = box2
    return range_overlap(l1, r1, l2, r2) and range_overlap(t1, b1, t2, b2)


box1 = [0, 0, 64, 64]
box2 = [64, 0, 128, 64]
box3 = [128, 0, 192, 64]
box4 = [192, 0, 256, 64]


def test_range_overlap_over12():
    viewport = [0, 0, 128, 64]
    assert overlap(viewport, box1) is True
    assert overlap(viewport, box2) is True
    assert overlap(viewport, box3) is False
    assert overlap(viewport, box4) is False


def test_range_overlap_over123():
    viewport = [30, 0, 158, 64]
    assert overlap(viewport, box1) is True
    assert overlap(viewport, box2) is True
    assert overlap(viewport, box3) is True
    assert overlap(viewport, box4) is False


def test_range_overlap_over23():
    viewport = [64, 0, 192, 64]
    assert overlap(viewport, box1) is False
    assert overlap(viewport, box2) is True
    assert overlap(viewport, box3) is True
    assert overlap(viewport, box4) is False


def test_range_overlap_over234():
    viewport = [100, 0, 228, 64]
    assert overlap(viewport, box1) is False
    assert overlap(viewport, box2) is True
    assert overlap(viewport, box3) is True
    assert overlap(viewport, box4) is True


def test_range_overlap_over34():
    viewport = [128, 0, 256, 64]
    assert overlap(viewport, box1) is False
    assert overlap(viewport, box2) is False
    assert overlap(viewport, box3) is True
    assert overlap(viewport, box4) is True


def test_range_overlap_over4():
    viewport = [192, 0, 256, 64]
    assert overlap(viewport, box1) is False
    assert overlap(viewport, box2) is False
    assert overlap(viewport, box3) is False
    assert overlap(viewport, box4) is True


def test_range_overlap_over_none():
    viewport = [256, 0, 384, 64]
    assert overlap(viewport, box1) is False
    assert overlap(viewport, box2) is False
    assert overlap(viewport, box3) is False
    assert overlap(viewport, box4) is False


def test_snapshot_last_updated():
    interval = 0.5

    def draw_fn(draw, width, height):
        assert height == 10
        assert width == 10

    sshot = snapshot(10, 10, draw_fn, interval)
    assert sshot.last_updated == -interval
    assert sshot.should_redraw() is True
    sshot.paste_into(Image.new("RGB", (10, 10)), (0, 0))
    assert sshot.should_redraw() is False
    time.sleep(interval * 1.5)
    assert sshot.should_redraw() is True
    sshot.paste_into(Image.new("RGB", (10, 10)), (0, 0))
    assert sshot.last_updated > 0.0
    assert sshot.should_redraw() is False


def test_viewport_set_position():
    img_path = get_reference_image('set_position.png')

    with open(img_path, 'rb') as p:
        reference = Image.open(p)
        device = dummy()
        virtual = viewport(device, 200, 200)

        # Use the same drawing primitives as the demo
        with canvas(virtual) as draw:
            baseline_data.primitives(virtual, draw)

        virtual.set_position((20, 30))

        assert_identical_image(reference, device.image, img_path)


def test_viewport_hotspot():
    img_path = get_reference_image('hotspot.png')

    with open(img_path, 'rb') as p:
        reference = Image.open(p)
        device = dummy()
        virtual = viewport(device, 200, 200)

        def draw_fn(draw, width, height):
            baseline_data.primitives(device, draw)

        widget = hotspot(device.width, device.height, draw_fn)

        virtual.add_hotspot(widget, (19, 56))
        virtual.set_position((28, 30))
        virtual.remove_hotspot(widget, (19, 56))

        assert_identical_image(reference, device.image, img_path)


def test_viewport_dithering():
    img_path = get_reference_image('hotspot_dither.png')

    with open(img_path, 'rb') as p:
        reference = Image.open(p)
        device = dummy(mode="1")
        virtual = viewport(device, 200, 200, mode='RGBA', dither=True)

        def draw_fn(draw, width, height):
            draw.rectangle((0, 0, width / 2, height / 2), fill="red")
            draw.rectangle((width / 2, 0, width, height / 2), fill="yellow")
            draw.rectangle((0, height / 2, width / 2, height), fill="blue")
            draw.rectangle((width / 2, height / 2, width, height), fill="white")

        widget = hotspot(device.width, device.height, draw_fn)

        virtual.add_hotspot(widget, (19, 56))
        virtual.set_position((28, 30))
        virtual.remove_hotspot(widget, (19, 56))

        assert_identical_image(reference, device.image, img_path)
