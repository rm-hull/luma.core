# -*- coding: utf-8 -*-
# Copyright (c) 2014-17 Richard Hull and contributors
# See LICENSE.rst for details.

import time
from PIL import Image


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
    constructor with the following attributes:

        * ``image``: a string representing the path to a sprite map image.
        * ``frames``: a dictionary of settings that defines how to extract
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

        * ``animations``: a dictionary of key/value pairs where the key is the
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

    Loosely based on http://www.createjs.com/docs/easeljs/classes/SpriteSheet.html
    """
    def __init__(self, **kwargs):
        self.animations = dict_wrapper(kwargs['animations'])
        self.frames = dict_wrapper(kwargs['frames'])
        self.image = Image.open(kwargs['image'])
        # Reframe the sprite map in terms of the registration point (if set)
        regX = self.frames.regX if hasattr(self.frames, "regX") else 0
        regY = self.frames.regY if hasattr(self.frames, "regY") else 0
        self.image = self.image.crop((regX, regY, self.image.width - regX, self.image.height - regY))
        self.width, self.height = self.image.size

        assert(self.width % self.frames.width == 0)
        assert(self.height % self.frames.height == 0)

        self.frames.size = (self.frames.width, self.frames.height)
        if not hasattr(self.frames, 'count'):
            self.frames.count = (self.width * self.height) // (self.frames.width * self.frames.height)

        self.cache = {}

    def __getitem__(self, key):
        """
        Returns (and caches) the given frame. If a value outside the range is
        given, an ``IndexError`` is raised.
        """

        if not isinstance(key, int):
            raise TypeError("frame index must be numeric")

        if key < 0 or key > self.frames.count:
            raise IndexError("frame index out of range")

        cached_frame = self.cache.get(key)
        if cached_frame is None:
            offset = key * self.frames.width
            left = offset % self.width
            top = (offset // self.width) * self.frames.height
            right = left + self.frames.width
            bottom = top + self.frames.height

            bounds = [left, top, right, bottom]
            cached_frame = self.image.crop(bounds)
            self.cache[key] = cached_frame

        return cached_frame

    def __len__(self):
        """
        The number of frames in the sprite sheet
        """
        return self.frames.count

    def animate(self, key):
        """
        Returns a generator which "executes" an animation sequence for the given
        key, inasmuch as the next frame for the given animation is yielded when
        requested.
        """
        while True:
            index = 0
            anim = getattr(self.animations, key)
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

            key = anim.next


class framerate_regulator(object):
    """
    Implements a variable sleep mechanism to give the appearance of a consistent
    frame rate. Using a fixed-time sleep will cause animations to be jittery
    (looking like they are speeding up or slowing down, depending on what other
    work is occurring), whereas this class keeps track of when the last time the
    ``sleep()`` method was called, and calculates a sleep period to smooth out
    the jitter.

    By default the ``fps`` argument (frames-per-second) is set at 16.67, to give
    a frame render time of 60ms. This can be overriden to user needs, and if no
    FPS limiting is required, the ``fps`` can be set to zero.
    """
    def __init__(self, fps=16.67):
        if fps == 0:
            fps = -1

        self.max_sleep_time = 1.0 / fps
        self.start_time = time.time()
        self.last_time = self.start_time
        self.called = 0

    def sleep(self):
        """
        Sleeps for a variable amount of time (dependent on when it was last
        called), to give a consistent frame rate. If it cannot meet the desired
        frame rate (i.e. too much time has occurred since the last call), then
        it simply exits without blocking.
        """
        self.called += 1
        elapsed = time.time() - self.last_time
        sleep_for = self.max_sleep_time - elapsed

        if sleep_for > 0:
            time.sleep(sleep_for)

        self.last_time = time.time()

    def effective_FPS(self):
        """
        Calculates the effective frames-per-second - this should largely
        correlate to the desired FPS supplied in the constructor, but no
        guarantees are given.
        """
        elapsed = time.time() - self.start_time
        return self.called / elapsed
