#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.virtual.terminal` class.
"""

import os.path
from PIL import Image, ImageChops

from luma.core.device import dummy
from luma.core.virtual import terminal


def test_wrapped_text():
    reference = Image.open(
        os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            'reference',
            'quick_brown_fox.png')))

    device = dummy()
    term = terminal(device)

    term.println("The quick brown fox jumps over the lazy dog")

    bbox = ImageChops.difference(reference, device.image).getbbox()
    assert bbox is None


def test_tab_alignment():
    reference = Image.open(
        os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            'reference',
            'tab_align.png')))

    device = dummy()
    term = terminal(device, animate=False)

    term.println("1\t32\t999")
    term.println("999\t1\t32")

    bbox = ImageChops.difference(reference, device.image).getbbox()
    assert bbox is None


def test_control_chars():
    reference = Image.open(
        os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            'reference',
            'control_chars.png')))

    device = dummy()
    term = terminal(device, animate=False)

    term.println('foo\rbar\bspam\teggs\n\nham and cheese on rye')

    bbox = ImageChops.difference(reference, device.image).getbbox()
    assert bbox is None


def test_scrolling():
    reference = Image.open(
        os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            'reference',
            'scroll_text.png')))

    device = dummy()
    term = terminal(device, animate=False)

    term.println(
        "it oozed over the blackness, and heard Harris's sleepy voice asking " +
        "where we drew near it, so they spread their handkerchiefs on the back " +
        "of Harris and Harris's friend as to avoid running down which, we managed " +
        "to get out of here while this billing and cooing is on. We'll go down " +
        "to eat vegetables. He said they were demons.")

    bbox = ImageChops.difference(reference, device.image).getbbox()
    assert bbox is None


def test_alt_colors():
    reference = Image.open(
        os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            'reference',
            'alt_colors.png')))

    device = dummy()
    term = terminal(device, color="blue", bgcolor="grey", animate=False)

    term.println("blue on grey")

    bbox = ImageChops.difference(reference, device.image).getbbox()
    assert bbox is None
