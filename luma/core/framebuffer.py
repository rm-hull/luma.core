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
    bounding box describing the areas that are different, up to the size of the
    entire image.

    The image data for the difference is then be passed to a device for
    rendering just those small changes. This can be very quick for small screen
    updates, but suffers from variable render times, depending on the changes
    applied. The :py:class`luma.core.sprite_system.framerate_regulator` may be
    used to counteract this behavior however.

    :param device: the target device, used to determine the initial 'previous'
        image.
    :type device: luma.core.device.device
    """
    def __init__(self, device):
        self.image = Image.new(device.mode, device.size, "white")
        self.bounding_box = None

    def redraw_required(self, image):
        """
        Calculates the difference from the previous image, return a boolean
        indicating whether a redraw is required. A side effect is that
        ``bounding_box`` and ``image`` attributes are updated accordingly, as is
        priming :py:func:`getdata`.

        :param image: An image to render
        :type image: PIL.Image.Image
        :returns: ``True`` or ``False``
        """
        self.bounding_box = ImageChops.difference(self.image, image).getbbox()
        if self.bounding_box is not None:
            self.image = image.copy()
            return True
        else:
            return False

    def inflate_bbox(self):
        """
        Realign the left and right edges of the bounding box such that they are
        inflated to align modulo 4.

        This method is optional, and used mainly to accommodate devices with
        COM/SEG GDDRAM structures that store pixels in 4-bit nibbles.
        """
        left, top, right, bottom = self.bounding_box
        self.bounding_box = (
            left & 0xFFFC,
            top,
            right if right % 4 == 0 else (right & 0xFFFC) + 0x04,
            bottom)

        return self.bounding_box

    def getdata(self):
        """
        A sequence of pixel data relating to the changes that occurred
        since the last time :py:func:`redraw_required` was last called.

        :returns: A sequence of pixels or ``None``
        :rtype: iterable
        """
        if self.bounding_box:
            return self.image.crop(self.bounding_box).getdata()


class full_frame(object):
    """
    Always renders the full frame every time. This is slower than
    :py:class:`diff_to_previous` as there are generally more
    pixels to update on every render, but it has a more consistent render time.
    Not all display drivers may be able to use the differencing framebuffer, so
    this is provided as a drop-in replacement.

    :param device: The target device, used to determine the bounding box.
    :type device: luma.core.device.device
    """
    def __init__(self, device):
        self.bounding_box = (0, 0, device.width, device.height)

    def redraw_required(self, image):
        """
        Caches the image ready for getting the sequence of pixel data with
        :py:func:`getdata`. This method always returns affirmatively.

        :param image: An image to render
        :type image: PIL.Image.Image
        :returns: ``True`` always.
        """
        self.image = image
        return True

    def inflate_bbox(self):
        """
        Just return the original bounding box without any inflation.
        """
        return self.bounding_box

    def getdata(self):
        """
        A sequence of pixels representing the full image supplied when the
        :py:func:`redraw_required` method was last called.

        :returns: A sequence of pixels
        :rtype: iterable
        """
        return self.image.getdata()
