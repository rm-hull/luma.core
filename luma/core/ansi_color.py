# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
ANSI Escape-code parser

.. versionadded:: 0.5.5
"""

import re


valid_attributes = {
    # Text attributes
    0: ["reset"],
    7: ["reverse_colors"],

    # Foreground colors
    30: ["foreground_color", "black"],
    31: ["foreground_color", "red"],
    32: ["foreground_color", "green"],
    33: ["foreground_color", "yellow"],
    34: ["foreground_color", "blue"],
    35: ["foreground_color", "magenta"],
    36: ["foreground_color", "cyan"],
    37: ["foreground_color", "white"],

    # Background colors
    40: ["background_color", "black"],
    41: ["background_color", "red"],
    42: ["background_color", "green"],
    43: ["background_color", "yellow"],
    44: ["background_color", "blue"],
    45: ["background_color", "magenta"],
    46: ["background_color", "cyan"],
    47: ["background_color", "white"],
}


def parse_str(text):
    """
    Given a string of characters, for each normal ASCII character, yields
    a directive consisting of a 'putch' instruction followed by the character
    itself.

    If a valid ANSI escape sequence is detected within the string, the
    supported codes are translated into directives. For example ``\\033[42m``
    would emit a directive of ``["background_color", "green"]``.

    Note that unrecognised escape sequences are silently ignored: Only reset,
    reverse colours and 8 foreground and background colours are supported.

    It is up to the consumer to interpret the directives and update its state
    accordingly.

    :param text: An ASCII string which may or may not include valid ANSI Color
        escape codes.
    :type text: str
    """
    prog = re.compile(r'^\033\[(\d+(;\d+)*)m', re.UNICODE)

    while text != "":
        result = prog.match(text)
        if result:
            for code in result.group(1).split(";"):
                directive = valid_attributes.get(int(code), None)
                if directive:
                    yield directive
            n = len(result.group(0))
            text = text[n:]
        else:
            yield ["putch", text[0]]
            text = text[1:]


def strip_ansi_codes(text):
    """
    Remove ANSI color codes from the string ``text``.

    .. versionadded:: 0.9.0

    :param text: String containing ANSI color codes.
    :type text: str
    :rtype: str
    """
    return re.sub('\033\\[([0-9]+)(;[0-9]+)*m', '', text)


def find_directives(text, klass):
    """
    Find directives on class ``klass`` in string ``text``.

    Returns list of ``(method, args)`` tuples.

    .. versionadded:: 0.9.0

    :param text: String containing directives.
    :type text: str
    :type klass: object
    :rtype: list
    """
    directives = []
    for directive in parse_str(text):
        method = klass.__getattribute__(directive[0])
        args = directive[1:]
        directives.append((method, args))
    return directives
