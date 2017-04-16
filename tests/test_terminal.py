#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.virtual.terminal` class.
"""

from PIL import Image, ImageChops

from luma.core.device import dummy
from luma.core.virtual import terminal

from helpers import get_reference_image


def test_default_text():
    img_path = get_reference_image('quick_brown_fox.png')

    with open(img_path, 'rb') as p:
        reference = Image.open(p)
        device = dummy()
        term = terminal(device)

        term.println("The quick brown fox jumps over the lazy dog")

        bbox = ImageChops.difference(reference, device.image).getbbox()
        assert bbox is None


def test_wrapped_text():
    img_path = get_reference_image('quick_brown_fox_word_wrap.png')

    with open(img_path, 'rb') as p:
        reference = Image.open(p)
        device = dummy()
        term = terminal(device, word_wrap=True)

        term.println("The quick brown fox jumps over the lazy dog")

        bbox = ImageChops.difference(reference, device.image).getbbox()
        assert bbox is None


def test_tab_alignment():
    img_path = get_reference_image('tab_align.png')

    with open(img_path, 'rb') as p:
        reference = Image.open(p)
        device = dummy()
        term = terminal(device, animate=False)

        term.println("1\t32\t999")
        term.println("999\t1\t32")

        bbox = ImageChops.difference(reference, device.image).getbbox()
        assert bbox is None


def test_control_chars():
    img_path = get_reference_image('control_chars.png')

    with open(img_path, 'rb') as p:
        reference = Image.open(p)
        device = dummy()
        term = terminal(device, animate=False)

        term.println('foo\rbar\bspam\teggs\n\nham and cheese on rye')

        bbox = ImageChops.difference(reference, device.image).getbbox()
        assert bbox is None


def test_scrolling():
    img_path = get_reference_image('scroll_text.png')

    with open(img_path, 'rb') as p:
        reference = Image.open(p)
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
    img_path = get_reference_image('alt_colors.png')

    with open(img_path, 'rb') as p:
        reference = Image.open(p)
        device = dummy()
        term = terminal(device, color="blue", bgcolor="grey", animate=False)

        term.println("blue on grey")

        bbox = ImageChops.difference(reference, device.image).getbbox()
        assert bbox is None


def test_ansi_colors():
    img_path = get_reference_image('ansi_colors.png')

    with open(img_path, 'rb') as p:
        reference = Image.open(p)
        device = dummy()
        term = terminal(device)

        term.println("hello \033[31mworld\33[0m")
        term.println("this is \033[7mreversed\033[7m!")
        term.println("\033[45;37mYellow\033[0m \033[43;30mMagenta")

        bbox = ImageChops.difference(reference, device.image).getbbox()
        assert bbox is None
