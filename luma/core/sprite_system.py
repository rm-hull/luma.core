# -*- coding: utf-8 -*-
# Copyright (c) 2017-2022 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Simplified sprite animation framework.

.. note:: This module is an evolving "work-in-progress" and should be treated
          as such until such time as this notice disappears.
"""

from time import sleep
from PIL import Image

from luma.core.util import perf_counter


class dict_wrapper(object):
    """
    Helper class to turn dictionaries into objects.
    """
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [dict_wrapper(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, dict_wrapper(b) if isinstance(b, dict) else b)


class spritesheet(object):
    """
    A sprite sheet is a series of images (usually animation frames) combined
    into a larger image. A dictionary is usually spread into the object
    constructor parameters with the following top-level attributes:

    :param image: A path to a sprite map image.
    :type image: str

    :param frames: A dictionary of settings that defines how to extract
        individual frames from the supplied image, as follows

        - ``width`` & ``height`` are required and specify the dimensions of
          the frames
        - ``regX`` & ``regY`` indicate the registration point or "origin" of
          the frames
        - ``count`` allows you to specify the total number of frames in the
          spritesheet; if omitted, this will be calculated based on the
          dimensions of the source images and the frames. Frames will be
          assigned indexes based on their position in the source images
          (left to right, top to bottom).
    :type frames: dict

    :param animations: A dictionary of key/value pairs where the key is the
        name of of the animation sequence, and the value are settings that
        defines an animation sequence as follows:

        - ``frames`` is a list of frame to show in sequence. Usually this
          comprises of frame numbers, but can refer to other animation
          sequences (which are handled much like a subroutine call).
        - ``speed`` determines how quickly the animation frames are cycled
          through compared to the how often the animation sequence yields.
        - ``next`` is optional, but if supplied, determines what happens when
          the animation sequence is exhausted. Typically this can be used to
          self-reference, so that it forms an infinite loop, but can hand off
          to any other animation sequence.
    :type animations: dict

    Loosely based on https://www.createjs.com/docs/easeljs/classes/SpriteSheet.html
    """
    def __init__(self, image, frames, animations):
        with open(image, 'rb') as fp:
            self.image = Image.open(fp)
            self.image.load()
        self.frames = dict_wrapper(frames)
        self.animations = dict_wrapper(animations)
        # Reframe the sprite map in terms of the registration point (if set)
        regX = self.frames.regX if hasattr(self.frames, "regX") else 0
        regY = self.frames.regY if hasattr(self.frames, "regY") else 0
        self.image = self.image.crop((regX, regY, self.image.width - regX, self.image.height - regY))
        self.width, self.height = self.image.size

        assert self.width % self.frames.width == 0
        assert self.height % self.frames.height == 0

        self.frames.size = (self.frames.width, self.frames.height)
        if not hasattr(self.frames, 'count'):
            self.frames.count = (self.width * self.height) // (self.frames.width * self.frames.height)

        self.cache = {}

    def __getitem__(self, frame_index):
        """
        Returns (and caches) the frame for the given index.
        :param frame_index: The index of the frame.
        :type frame_index: int
        :returns: A Pillow image cropped from the main image corresponding to
            the given frame index.
        :raises TypeError: if the ``frame_index`` is not numeric
        :raises IndexError: if the ``frame_index`` is less than zero or more
            than the largest frame.
        """

        if not isinstance(frame_index, int):
            raise TypeError("frame index must be numeric")

        if frame_index < 0 or frame_index > self.frames.count:
            raise IndexError("frame index out of range")

        cached_frame = self.cache.get(frame_index)
        if cached_frame is None:
            offset = frame_index * self.frames.width
            left = offset % self.width
            top = (offset // self.width) * self.frames.height
            right = left + self.frames.width
            bottom = top + self.frames.height

            bounds = [left, top, right, bottom]
            cached_frame = self.image.crop(bounds)
            self.cache[frame_index] = cached_frame

        return cached_frame

    def __len__(self):
        """
        The number of frames in the sprite sheet
        """
        return self.frames.count

    def animate(self, seq_name):
        """
        Returns a generator which "executes" an animation sequence for the given
        ``seq_name``, inasmuch as the next frame for the given animation is
        yielded when requested.

        :param seq_name: The name of a previously defined animation sequence.
        :type seq_name: str
        :returns: A generator that yields all frames from the animation
            sequence.
        :raises AttributeError: If the ``seq_name`` is unknown.
        """
        while True:
            index = 0
            anim = getattr(self.animations, seq_name)
            speed = anim.speed if hasattr(anim, "speed") else 1
            num_frames = len(anim.frames)
            while index < num_frames:
                frame = anim.frames[int(index)]
                index += speed

                if isinstance(frame, int):
                    yield self[frame]
                else:
                    for subseq_frame in self.animate(frame):
                        yield subseq_frame

            if not hasattr(anim, "next"):
                break

            seq_name = anim.next


class framerate_regulator(object):
    """
    Implements a variable sleep mechanism to give the appearance of a consistent
    frame rate. Using a fixed-time sleep will cause animations to be jittery
    (looking like they are speeding up or slowing down, depending on what other
    work is occurring), whereas this class keeps track of when the last time the
    ``sleep()`` method was called, and calculates a sleep period to smooth out
    the jitter.

    :param fps: The desired frame rate, expressed numerically in
        frames-per-second.  By default, this is set at 16.67, to give a frame
        render time of approximately 60ms. This can be overridden as necessary,
        and if no FPS limiting is required, the ``fps`` can be set to zero.
    :type fps: float
    """
    def __init__(self, fps=16.67):
        if fps == 0:
            fps = -1

        self.max_sleep_time = 1.0 / fps
        self.total_transit_time = 0
        self.called = 0
        self.start_time = None
        self.last_time = None

    def __enter__(self):
        self.enter_time = perf_counter()
        if not self.start_time:
            self.start_time = self.enter_time
            self.last_time = self.enter_time

        return self

    def __exit__(self, *args):
        """
        Sleeps for a variable amount of time (dependent on when it was last
        called), to give a consistent frame rate. If it cannot meet the desired
        frame rate (i.e. too much time has occurred since the last call), then
        it simply exits without blocking.
        """
        self.called += 1
        self.total_transit_time += perf_counter() - self.enter_time
        if self.max_sleep_time >= 0:
            elapsed = perf_counter() - self.last_time
            sleep_for = self.max_sleep_time - elapsed

            if sleep_for > 0:
                sleep(sleep_for)

        self.last_time = perf_counter()

    def effective_FPS(self):
        """
        Calculates the effective frames-per-second - this should largely
        correlate to the desired FPS supplied in the constructor, but no
        guarantees are given.

        :returns: The effective frame rate.
        :rtype: float
        """
        if self.start_time is None:
            self.start_time = 0
        elapsed = perf_counter() - self.start_time
        return self.called / elapsed

    def average_transit_time(self):
        """
        Calculates the average transit time between the enter and exit methods,
        and return the time in milliseconds.

        :returns: The average transit in milliseconds.
        :rtype: float
        """
        return self.total_transit_time * 1000.0 / self.called
