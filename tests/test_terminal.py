#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:class:`luma.core.virtual.terminal` class.
"""

from PIL import Image

from luma.core.device import dummy
from luma.core.virtual import terminal

from helpers import (get_reference_image, assert_identical_image,
    get_reference_font)


def assert_text(device, term, reference_img, text, save=None):
    img_path = get_reference_image(reference_img)

    with open(img_path, 'rb') as fp:
        reference = Image.open(fp)

        for line in text:
            term.println(line)

        if save is not None:
            device.image.save(save)

        assert_identical_image(reference, device.image, img_path)


def test_default_text():
    reference = 'quick_brown_fox.png'
    device = dummy()
    term = terminal(device)

    assert_text(device, term, reference, [
        "The quick brown fox jumps over the lazy dog"
    ])


def test_wrapped_text():
    reference = 'quick_brown_fox_word_wrap.png'
    device = dummy()
    term = terminal(device, word_wrap=True, animate=False)

    assert_text(device, term, reference, [
        "The quick brown fox jumps over the lazy dog"
    ])


def test_tab_alignment():
    reference = 'tab_align.png'
    device = dummy()
    term = terminal(device, animate=False)

    assert_text(device, term, reference, [
        "1\t32\t999",
        "999\t1\t32"
    ])


def test_control_chars():
    reference = 'control_chars.png'
    device = dummy()
    term = terminal(device, animate=False)

    assert_text(device, term, reference, [
        'foo\rbar\bspam\teggs\n\nham and cheese on rye'
    ])


def test_scrolling():
    reference = 'scroll_text.png'
    device = dummy()
    term = terminal(device, animate=False)

    assert_text(device, term, reference, [
        "it oozed over the blackness, and heard Harris's sleepy voice asking "
        "where we drew near it, so they spread their handkerchiefs on the back "
        "of Harris and Harris's friend as to avoid running down which, we managed "
        "to get out of here while this billing and cooing is on. We'll go down "
        "to eat vegetables. He said they were demons."
    ])


def test_alt_colors():
    reference = 'alt_colors.png'
    device = dummy()
    term = terminal(device, color="blue", bgcolor="grey", animate=False)

    assert_text(device, term, reference, [
        "blue on grey"
    ])


def test_ansi_colors():
    reference = 'ansi_colors.png'
    device = dummy()
    term = terminal(device, animate=False)

    assert_text(device, term, reference, [
        "hello \033[31mworld\033[0m ansi colors here!",
        "this is \033[7mreversed\033[7m!",
        "\033[44;37mBlue\033[0m \033[46;30mCyan"
    ])


def test_ansi_colors_wrapped():
    reference = 'ansi_colors_wrapped.png'
    device = dummy()
    term = terminal(device, word_wrap=True, animate=False)

    assert_text(device, term, reference, [
        "hello \033[31mworld\033[0m ansi colors\t\033[32mwrap\033[0m\t?",
        "this is \033[7mreversed\033[7m!",
        "\033[43;30mYellow\033[0m \033[45;37mMagenta"
    ])


def test_ansi_colors_scroll():
    reference = 'ansi_colors_scroll.png'
    device = dummy()
    term = terminal(device, word_wrap=True, animate=False)

    assert_text(device, term, reference, [
        "hello \033[31mworld\033[0m ansi colors\t\033[32mwrap\033[0m\t?",
        "this is \033[7mreversed\033[7m!",
        "\033[43;30mYellow\033[0m \033[44;37mBlue abcdefg hijklmn",
        "\033[41;30mRed\033[0m \033[42;37mGreen"
    ])


def test_accented_charset():
    reference = 'accented_charset.png'
    unicode_font = get_reference_font('DejaVuSans.ttf')
    device = dummy()
    term = terminal(device, font=unicode_font, word_wrap=False, animate=False,
        color="blue", bgcolor="white")

    assert_text(device, term, reference, [
        u"\033[31mFußgängerunterführungen\033[0m Текст на русском"
    ])
