# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Different implementation strategies for framebuffering
"""

import math
from PIL import ImageChops


class diff_to_previous(object):
    """
    Compare the current frame to the previous frame and tries to calculate the
    differences: this will either yield nothing for a perfect match or else
    the iterator will yield one or more tuples comprising of the image part that
    changed along with the bounding box that describes the areas that are different,
    up to the size of the entire image.

    The image data for the difference is then be passed to a device for
    rendering just those small changes. This can be very quick for small screen
    updates, but suffers from variable render times, depending on the changes
    applied. The :py:class:`luma.core.sprite_system.framerate_regulator` may be
    used to counteract this behavior however.

    :param device: The target device, used to determine the initial 'previous'
        image.
    :type device: luma.core.device.device
    :param num_segments: The number of segments to partition the image into. This
        generally must be a square number (1, 4, 9, 16, ...) and must be able to
        segment the image entirely in both width and height. i.e setting to 9 will
        subdivide the image into a 3x3 grid when comparing to the previous image.
    :type num_segments: int
    """

    def __init__(self, num_segments=4):
        self.__n = int(math.sqrt(num_segments))
        assert num_segments >= 1 and num_segments == self.__n ** 2
        self.prev_image = None

    def redraw(self, image):
        """
        Calculates the difference from the previous image, returning a sequence of
        image sections and bounding boxes that changed since the previous image.
        Note that the first render will always render the full frame.

        :param image: The image to render.
        :type image: PIL.Image.Image
        :returns: Yields a sequence of images and the bounding box for each segment difference
        :rtype: Generator[Tuple[PIL.Image.Image, Tuple[int, int, int, int]]]
        """
        image_width, image_height = image.size
        segment_width = int(image_width / self.__n)
        segment_height = int(image_height / self.__n)
        assert segment_width * self.__n == image_width, "Total segment width does not cover full image width"
        assert segment_height * self.__n == image_height, "Total segment height does not cover full image height"
        
        changes = 0

        # Force a full redraw on the first frame
        if self.prev_image is None:
            changes += 1
            yield image, (0, 0, image_width, image_height)

        else:
            for x in range(0, image_width, segment_width):
                for y in range(0, image_height, segment_height):
                    bounding_box = (x, y, x + segment_width, y + segment_height)
                    prev_segment = self.prev_image.crop(bounding_box)
                    curr_segment = image.crop(bounding_box)
                    segment_bounding_box = ImageChops.difference(prev_segment, curr_segment).getbbox()
                    if segment_bounding_box is not None:
                        changes += 1
                        segment_bounding_box_from_origin = (
                            x + segment_bounding_box[0],
                            y + segment_bounding_box[1],
                            x + segment_bounding_box[2],
                            y + segment_bounding_box[3]
                        )
                        yield curr_segment.crop(segment_bounding_box), segment_bounding_box_from_origin

        if changes > 0:
            self.prev_image = image.copy()


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

    def __init__(self, **kwargs):
        pass

    def redraw(self, image):
        """
        Caches the image ready for getting the sequence of pixel data with
        :py:func:`getdata`. This method always returns affirmatively.

        :param image: The image to render.
        :type image: PIL.Image.Image
        :returns: Yields a single typle of sequence of images and the bounding box for that segment
        :rtype: Generator[Tuple[PIL.Image.Image, Tuple[int, int, int, int]]]
        """
        yield image, (0, 0, image.size[0], image.size[1])
