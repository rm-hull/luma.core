# -*- coding: utf-8 -*-
# Copyright (c) 2014-17 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Different implementation strategies for framebuffering
"""

from PIL import Image, ImageChops


class diff_to_previous(object):
    """
    Compare the current frame to the previous frame and tries to calculate the
    differences: this will either be ``None`` for a perfect match or some
    bounding box describing the areas that are different, upto the size of the
    entire image.

    The image data for the difference is then be passed to a device for
    rendering just those small changes. This can be very quick for small screen
    updates, but suffers from variable render times, depending on the changes
    applied. The :py:class`luma.core.sprite_system.framerate_regulator` may be
    used to counteract this behviour however.

    :param device: the target device, used to determine the initial 'previous'
        image.
    :type device: luma.core.device.device
    """
    def __init__(self, device):
        self.image = Image.new(device.mode, device.size, "white")

    def update(self, image):
        """
        Calculates the difference from the previous image, setting ``bbox`` and
        ``image`` attributes, and priming :py:func:`getdata`.

        :param image: An image to render
        :type image: PIL.Image.Image
        """
        self.bbox = ImageChops.difference(self.image, image).getbbox()
        if self.bbox is not None:
            self.image = image.copy()

    def getdata(self):
        """
        A sequence of pixel data relating to the changes that occurred
        since the last time :py:func:`update` was last called.

        :returns: A sequence of pixels
        """
        return self.image.crop(self.bbox).getdata() if self.bbox else []


class full_frame(object):
    """
    Always renders the full frame every time. This is slower than
    :py:class:`diff_to_previous` as there are generally more
    pixels to update on every render, but it has a more consistent render time.
    Not all display drivers may be able to use the differencing framebuffer, so
    this is provided as a drop-in replacement.

    :param device: the target device, used to determine the bounding box.
    :type device: luma.core.device.device
    """
    def __init__(self, device):
        self.bbox = (0, 0, device.width, device.height)

    def update(self, image):
        """
        Caches the image ready for getting the sequence of pixel data with
        :py:func:`getdata`.

        :param image: An image to render
        :type image: PIL.Image.Image
        """
        self.image = image

    def getdata(self):
        """
        A sequence of pixels representing the full image supplied to the
        :py:func:`update` method.

        :returns: A sequence of pixels
        """
        return self.image.getdata()
