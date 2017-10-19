# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

from PIL import Image, ImageDraw
from luma.core import mixin


class MultiImage(mixin.capabilities):
    '''
    Renders multiple images on a background
    '''

    image_id = 0

    def __init__(self, device, width, height):
        '''
        Instantiates a new MultiImage
        '''
        self.capabilities(width, height, rotate=0, mode=device.mode)
        self._device = device
        self._background_image = Image.new(self.mode, self.size)
        self.images = {}

    def get_size(self):
        return self._device.size

    def add_image(self, im, xy=(0, 0), offs=(0, 0)):
        '''
        Adds an image to the list of images to be rendered.
        Returns a unique image id
        '''
        id = MultiImage.image_id
        MultiImage.image_id += 1
        self.images[id] = (im, xy, offs)
        return id

    def remove_image(self, id):
        '''
        Removes an image from list of images to be rendered
        '''
        if id in self.images:
            del self.images[id]

    def set_position(self, id, xy):
        '''
        Sets the position of an image within the device boundaries
        '''
        if id in self.images:
            self.images[id] = (self.images[id][0], xy, self.images[id][2])
            self.refresh()

    def set_offset(self, id, offs):
        '''
        Selects an offset within the image from which to draw
        the image. This allows scrolling of the image, similar
        to viewport.
        The image is clipped at the device boundaries.
        '''
        if id in self.images:
            self.images[id] = (self.images[id][0], self.images[id][1], offs)
            self.refresh()

    def refresh(self):
        self.clear()
        for id, image in self.images.iteritems():
            pasted_im = image[0].crop(box=self._crop_box(image[0], image[2]))
            self._background_image.paste(pasted_im, image[1])
        im = self._background_image.crop(
            box=(0, 0, self._device.width, self._device.height))
        self._device.display(im)

    def clear(self):
        draw = ImageDraw.Draw(self._background_image)
        draw.rectangle(self._device.bounding_box,
                               fill="black")

    def _crop_box(self, image, offs):
        '''
        Calculates the crop box for the offset within an image
        '''
        (left, top) = offs
        right = left + min(self._device.width, image.width)
        bottom = top + min(self._device.height, image.height)

        return (left, top, right, bottom)
