# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

from PIL import Image, ImageDraw


class canvas(object):
    """
    A canvas returns a properly-sized :py:mod:`PIL.ImageDraw` object onto
    which the caller can draw upon. As soon as the with-block completes, the
    resultant image is flushed onto the device.

    By default, any color (other than black) will be `generally` treated as
    white when displayed on monochrome devices. However, this behaviour can be
    changed by adding ``dither=True`` and the image will be converted from RGB
    space into a 1-bit monochrome image where dithering is employed to
    differentiate colors at the expense of resolution.
    If a ``background`` parameter is provided, the canvas is based on the given
    background. This is useful to e.g. write text on a given background image.
    """
    def __init__(self, device, background=None, dither=False):
        """
        Initialize the device.

        Args:
            self: (todo): write your description
            device: (todo): write your description
            background: (array): write your description
            dither: (todo): write your description
        """
        self.draw = None
        if background is None:
            self.image = Image.new("RGB" if dither else device.mode, device.size)
        else:
            assert(background.size == device.size)
            self.image = background.copy()
        self.device = device
        self.dither = dither

    def __enter__(self):
        """
        Enter the image

        Args:
            self: (todo): write your description
        """
        self.draw = ImageDraw.Draw(self.image)
        return self.draw

    def __exit__(self, type, value, traceback):
        """
        Triggers the image.

        Args:
            self: (todo): write your description
            type: (todo): write your description
            value: (todo): write your description
            traceback: (todo): write your description
        """
        if type is None:

            if self.dither:
                self.image = self.image.convert(self.device.mode)

            # do the drawing onto the device
            self.device.display(self.image)

        del self.draw   # Tidy up the resources
        return False    # Never suppress exceptions
