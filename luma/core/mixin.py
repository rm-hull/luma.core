# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

from PIL import Image


class capabilities(object):
    """
    This class should be 'mixed-in' to any :py:class:`luma.core.device.device`
    display implementation that should have "device-like" capabilities.
    """
    def capabilities(self, width, height, rotate, mode="1"):
        """
        Assigns attributes such as ``width``, ``height``, ``size`` and
        ``bounding_box`` correctly oriented from the supplied parameters.

        :param width: the device width
        :type width: int
        :param height: the device height
        :type height: int
        :param rotate: an integer value of 0 (default), 1, 2 or 3 only, where 0 is
            no rotation, 1 is rotate 90° clockwise, 2 is 180° rotation and 3
            represents 270° rotation.
        :type rotate: int
        :param mode: the supported color model, one of "1", "RGB" or "RGBA" only.
        :type mode: str
        """
        assert mode in ("1", "RGB", "RGBA")
        assert rotate in (0, 1, 2, 3)
        self._w = width
        self._h = height
        self.width = width if rotate % 2 == 0 else height
        self.height = height if rotate % 2 == 0 else width
        self.size = (self.width, self.height)
        self.bounding_box = (0, 0, self.width - 1, self.height - 1)
        self.rotate = rotate
        self.mode = mode

    def clear(self):
        """
        Initializes the device memory with an empty (blank) image.
        """
        self.display(Image.new(self.mode, self.size))

    def preprocess(self, image):
        """
        Provides a preprocessing facility (which may be overridden) whereby the supplied image is
        rotated according to the device's rotate capability. If this method is
        overridden, it is important to call the super

        :param image: An image to pre-process
        :type image: PIL.Image.Image
        :returns: A new processed image
        :rtype: PIL.Image.Image
        """
        if self.rotate == 0:
            return image

        angle = self.rotate * -90
        return image.rotate(angle, expand=True).crop((0, 0, self._w, self._h))

    def display(self, image):
        """
        Should be overridden in sub-classed implementations.

        :param image: An image to display
        :type image: PIL.Image.Image
        :raises NotImplementedError:
        """
        raise NotImplementedError()
