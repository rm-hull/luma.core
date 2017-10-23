# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

# TODO: assertions

from PIL import Image, ImageDraw
from luma.core import mixin


class ComposableImage(object):
    """
    This class encapsulates an image and its attributes
    that can be rendered onto an ImageComposition
    """
    def __init__(self, image, position=(0, 0), offset=(0, 0)):
        """
        Instantiates a new ComposableImage
        :param image: the composable image
        :type image: Image
        :param position: the initial position of the image
            within the composition
        :type position: tuple
        :param offset: the initial offset within the image,
            from which it should be drawn
        :type offset: tuple
        """
        self._image = image
        self._position = position
        self._offset = offset

    @property
    def position(self):
        """
        Getter for position
        :returns: A tuple containing the x,y position
        :rtype: tuple
        """
        return self._position

    @position.setter
    def position(self, value):
        """
        Indicates where the image is to be rendered in an image
        composition
        :param value: The x,y position
        :type value: tuple
        """
        self._position = value

    @property
    def offset(self):
        """
        Getter for offset
        :returns: A tuple containing the top,left
        :rtype: tuple
        """
        return self._offset

    @offset.setter
    def offset(self, value):
        """
        Indicates the top left position within the image,
        as of which it is is to be rendered in the
        image composition
        :param value: The top,left position
        :type value: tuple
        """
        self._offset = value

    @property
    def width(self):
        """
        :returns: The actual width of the image, regardless
        its position or offset within the image composition
        :rtype: int
        """
        return self._image.width

    @property
    def height(self):
        """
        :returns: The actual height of the image, regardless
        its position or offset within the image composition
        :rtype: int
        """
        return self._image.height

    def image(self, dimensions):
        """
        :param dimensions: the width and height of the image composition
        :type dimensions: tuple
        :returns: An image, cropped to the boundaries specified
        by ``dimensions``
        :rtype: Image
        """
        return self._image.crop(box=self._crop_box(dimensions))

    def _crop_box(self, dimensions):
        """
        Helper that calculates the crop box for the offset within the image
        :param dimensions: the width and height of the image composition
        :type dimensions: tuple
        :returns: The bounding box of the image, given ```dimensions```
        :rtype: tuple
        """
        (left, top) = self.offset
        right = left + min(dimensions[0], self.width)
        bottom = top + min(dimensions[1], self.height)

        return (left, top, right, bottom)


class ImageComposition(mixin.capabilities):
    """
    Manages a composition of ComposableImages that
    can be rendered onto a single Image
    """

    def __init__(self, device, width, height):
        """
        Instantiates a new ImageComposition

        :param device: the device on which to render
        :type device: Device
        :param width: the width of the composition
        :type width: int
        :param height: the height of the composition
        :type height: int
        """
        self.capabilities(width, height, rotate=0, mode=device.mode)
        self._device = device
        self._background_image = Image.new(self.mode, self.size)
        self.composed_images = []

    def add_image(self, image):
        """
        Adds an image to the composition
        :param image: the image to add
        :type image: Image
        """
        self.composed_images.append(image)

    def remove_image(self, image):
        """
        Removes an image from the composition
        :param image: the image to be removed
        :type image: Image
        """
        self.composed_images.remove(image)

    def __call__(self):
        """
        Returns the current composition
        :rtype: Image
        """
        return self._background_image

    def refresh(self):
        """
        Clears the composition and renders all the images
        taking into account their position and offset
        """
        self._clear()
        for img in self.composed_images:
            self._background_image.paste(img.image(
                                  (self._device.width, self._device.height)),
                                  img.position)
        self._background_image.crop(box=self._device.bounding_box)

    def _clear(self):
        """
        Helper that clears the composition
        """
        draw = ImageDraw.Draw(self._background_image)
        draw.rectangle(self._device.bounding_box,
                       fill="black")
