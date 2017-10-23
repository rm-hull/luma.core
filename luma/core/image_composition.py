# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

# TODO: add doc
# TODO: assertions

from PIL import Image, ImageDraw
from luma.core import mixin


class ComposableImage(object):
    def __init__(self, image, dimensions=(0, 0),
                 position=(0, 0), offset=(0, 0)):
        self._image = image
        self._position = position
        self._offset = offset

    @property
    def position(self):
        """
        Sets the position of an image within the device boundaries
        """
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value

    @property
    def width(self):
        return self._image.width

    @property
    def height(self):
        return self._image.height

    def image(self, dimensions):
        return self._image.crop(box=self._crop_box(dimensions))

    def _crop_box(self, dimensions):
        """
        Calculates the crop box for the offset within the image
        """
        (left, top) = self.offset
        right = left + min(dimensions[0], self.width)
        bottom = top + min(dimensions[1], self.height)

        return (left, top, right, bottom)


class ImageComposition(mixin.capabilities):
    """
    Manages a composition of ComposableImages that can be
    individually moved and have their offset changed
    """

    def __init__(self, device, width, height):
        """
        Instantiates a new ImageComposition

        :param device: the device on which to render
        :type device: Device
        :param width: the width
        :type width: int
        :param height: the height
        :type height: int
        """
        self.capabilities(width, height, rotate=0, mode=device.mode)
        self._device = device
        self._background_image = Image.new(self.mode, self.size)
        self.composed_images = []

    def add_image(self, image):
        self.composed_images.append(image)

    def remove_image(self, image):
        self.composed_images.remove(image)

    def __call__(self):
        return self._background_image

    def refresh(self):
        self._clear()
        for img in self.composed_images:
            self._background_image.paste(img.image(
                                  (self._device.width, self._device.height)),
                                  img.position)
        self._background_image.crop(box=self._device.bounding_box)

    def _clear(self):
        draw = ImageDraw.Draw(self._background_image)
        draw.rectangle(self._device.bounding_box,
                       fill="black")
