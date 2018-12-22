# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Composes scrollable, positionable images into another
Image

.. versionadded:: 1.1.0
"""

from PIL import Image, ImageDraw


class ComposableImage(object):
    """
    This class encapsulates an image and its attributes
    that can be rendered onto an :py:class:`ImageComposition`.
    """
    def __init__(self, image, position=(0, 0), offset=(0, 0)):
        """
        Instantiates a new ``ComposableImage``.

        :param image: The composable image.
        :type image: PIL.Image
        :param position: The initial position of the image
            within the composition.
        :type position: tuple
        :param offset: The initial offset within the image,
            from which it should be drawn.
        :type offset: tuple
        """
        assert(image)
        self._image = image
        self._position = position
        self._offset = offset

    @property
    def position(self):
        """
        Getter for position

        :returns: A tuple containing the ``x,y`` position.
        :rtype: tuple
        """
        return self._position

    @position.setter
    def position(self, value):
        """
        Indicates where the image is to be rendered in an image
        composition.

        :param value: The ``x,y`` position tuple.
        :type value: tuple
        """
        self._position = value

    @property
    def offset(self):
        """
        Getter for offset.

        :returns: A tuple containing the top,left position.
        :rtype: tuple
        """
        return self._offset

    @offset.setter
    def offset(self, value):
        """
        Indicates the top left position within the image,
        as of which it is is to be rendered in the
        image composition.

        :param value: The top,left position.
        :type value: tuple
        """
        self._offset = value

    @property
    def width(self):
        """
        :returns: The actual width of the image, regardless
            its position or offset within the image composition.
        :rtype: int
        """
        return self._image.width

    @property
    def height(self):
        """
        :returns: The actual height of the image, regardless
            its position or offset within the image composition.
        :rtype: int
        """
        return self._image.height

    def image(self, size):
        """
        :param size: The width, height of the image composition.
        :type size: tuple
        :returns: An image, cropped to the boundaries specified
            by ``size``.
        :rtype: PIL.Image.Image
        """
        assert(size[0])
        assert(size[1])
        return self._image.crop(box=self._crop_box(size))

    def _crop_box(self, size):
        """
        Helper that calculates the crop box for the offset within the image.

        :param size: The width and height of the image composition.
        :type size: tuple
        :returns: The bounding box of the image, given ``size``.
        :rtype: tuple
        """
        (left, top) = self.offset
        right = left + min(size[0], self.width)
        bottom = top + min(size[1], self.height)

        return (left, top, right, bottom)


class ImageComposition(object):
    """
    Manages a composition of :py:class:`ComposableImage` instances that
    can be rendered onto a single :py:class:`PIL.Image.Image`.
    """
    def __init__(self, device):
        """
        Instantiates a new ``ImageComposition``

        :param device: The device on which to render.
        :type device: luma.core.device.device
        """
        self._device = device
        self._background_image = Image.new(device.mode, device.size)
        self.composed_images = []

    def add_image(self, image):
        """
        Adds an image to the composition.

        :param image: The image to add.
        :type image: PIL.Image.Image
        """
        assert(image)
        self.composed_images.append(image)

    def remove_image(self, image):
        """
        Removes an image from the composition.

        :param image: The image to be removed.
        :type image: PIL.Image.Image
        """
        assert(image)
        self.composed_images.remove(image)

    def __call__(self):
        """
        Returns the current composition.

        :rtype: PIL.Image.Image
        """
        return self._background_image

    def refresh(self):
        """
        Clears the composition and renders all the images
        taking into account their position and offset.
        """
        self._clear()
        for img in self.composed_images:
            self._background_image.paste(img.image(self._device.size),
                                         img.position)
        self._background_image.crop(box=self._device.bounding_box)

    def _clear(self):
        """
        Helper that clears the composition.
        """
        draw = ImageDraw.Draw(self._background_image)
        draw.rectangle(self._device.bounding_box,
                       fill="black")
        del draw
