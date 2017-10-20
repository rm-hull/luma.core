# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

from PIL import Image, ImageDraw
from luma.core import mixin

# TODO: rename xy -> pos
# TODO: rename offs -> offset

class RenderedImage():
    
    def __init__(self, image, xy=(0, 0), offs=(0, 0)):
        self.image = image
        self.xy = xy
        self.offs = offs
    
    def set_position(self, xy):
        """
        Sets the position of an image within the device boundaries
        """
        self.xy = xy

    def set_offset(self, offs):
        self.offs = offs

    def cropped_image(self, dimensions):
        return self.image.crop(box=self._crop_box(dimensions))

    def _crop_box(self, dimensions):
        """
        Calculates the crop box for the offset within the image
        """
        (left, top) = self.offs
        right = left + min(dimensions[0], self.image.width)
        bottom = top + min(dimensions[1], self.image.height)

        return (left, top, right, bottom)


class MultiImage(mixin.capabilities):
    """
    Renders multiple images on a background
    """

    image_id = 0 # FIXME remove

    def __init__(self, device, width, height):
        """
        Instantiates a new MultiImage

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
        self.images = {}
        self.rendered_images = []

    def image(self):
        return self._background_image

    def add_image(self, rendered_image):
        self.rendered_images.append(rendered_image)

    def remove_image(self, rendered_image):
        self.rendered_images.remove(rendered_image)
    
    def refresh(self):
        self._clear()
        for img in self.rendered_images:
            self._background_image.paste(img.cropped_image((self._device.width, self._device.height)), img.xy)
        self._background_image.crop(box = self._device.bounding_box)

    def _clear(self):
        draw = ImageDraw.Draw(self._background_image)
        draw.rectangle(self._device.bounding_box,
                               fill="black")
