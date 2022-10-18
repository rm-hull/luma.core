# -*- coding: utf-8 -*-
# Copyright (c) 2017-2022 Richard Hull and contributors
# See LICENSE.rst for details.

from time import sleep
from textwrap import TextWrapper

from PIL import Image, ImageDraw, ImageFont

from luma.core import mixin, ansi_color
from luma.core.threadpool import threadpool
from luma.core.render import canvas
from luma.core.util import mutable_string, observable, perf_counter


pool = threadpool(4)


def calc_bounds(xy, entity):
    """
    For an entity with width and height attributes, determine
    the bounding box if were positioned at ``(x, y)``.
    """
    left, top = xy
    right, bottom = left + entity.width, top + entity.height
    return [left, top, right, bottom]


def range_overlap(a_min, a_max, b_min, b_max):
    """
    Neither range is completely greater than the other.
    """
    return (a_min < b_max) and (b_min < a_max)


class viewport(mixin.capabilities):
    """
    The viewport offers a positionable window into a larger resolution pseudo-display,
    that also supports the concept of hotspots (which act like live displays).

    :param device: The device to project the enlarged pseudo-display viewport onto.
    :param width: The number of horizontal pixels.
    :type width: int
    :param height: The number of vertical pixels.
    :type height: int
    :param mode: The supported color model, one of ``"1"``, ``"RGB"`` or
        ``"RGBA"`` only.
    :type mode: str
    :param dither: By default, any color (other than black) will be `generally`
        treated as white when displayed on monochrome devices. However, this behaviour
        can be changed by adding ``dither=True`` and the image will be converted from RGB
        space into a 1-bit monochrome image where dithering is employed to differentiate
        colors at the expense of resolution.
    :type dither: bool
    """
    def __init__(self, device, width, height, mode=None, dither=False):
        self.capabilities(width, height, rotate=0, mode=mode or device.mode)
        if hasattr(device, "segment_mapper"):
            self.segment_mapper = device.segment_mapper
        self._device = device
        self._backing_image = Image.new(self.mode, self.size)
        self._position = (0, 0)
        self._hotspots = []
        self._dither = dither

    def display(self, image):
        assert image.mode == self.mode
        assert image.size == self.size

        self._backing_image.paste(image)
        self.refresh()

    def set_position(self, xy):
        self._position = xy
        self.refresh()

    def add_hotspot(self, hotspot, xy):
        """
        Add the hotspot at ``(x, y)``. The hotspot must fit inside the bounds
        of the virtual device. If it does not then an ``AssertError`` is
        raised.
        """
        (x, y) = xy
        assert 0 <= x <= self.width - hotspot.width
        assert 0 <= y <= self.height - hotspot.height

        # TODO: should it check to see whether hotspots overlap each other?
        # Is sensible to _allow_ them to overlap?
        self._hotspots.append((hotspot, xy))

    def remove_hotspot(self, hotspot, xy):
        """
        Remove the hotspot at ``(x, y)``: Any previously rendered image where
        the hotspot was placed is erased from the backing image, and will be
        "undrawn" the next time the virtual device is refreshed. If the
        specified hotspot is not found for ``(x, y)``, a ``ValueError`` is
        raised.
        """
        self._hotspots.remove((hotspot, xy))
        eraser = Image.new(self.mode, hotspot.size)
        self._backing_image.paste(eraser, xy)

    def is_overlapping_viewport(self, hotspot, xy):
        """
        Checks to see if the hotspot at position ``(x, y)``
        is (at least partially) visible according to the
        position of the viewport.
        """
        l1, t1, r1, b1 = calc_bounds(xy, hotspot)
        l2, t2, r2, b2 = calc_bounds(self._position, self._device)
        return range_overlap(l1, r1, l2, r2) and range_overlap(t1, b1, t2, b2)

    def refresh(self):
        should_wait = False
        for hotspot, xy in self._hotspots:
            if hotspot.should_redraw() and self.is_overlapping_viewport(hotspot, xy):
                pool.add_task(hotspot.paste_into, self._backing_image, xy)
                should_wait = True

        if should_wait:
            pool.wait_completion()

        im = self._backing_image.crop(box=self._crop_box())
        if self._dither:
            im = im.convert(self._device.mode)

        self._device.display(im)

    def _crop_box(self):
        (left, top) = self._position
        right = left + self._device.width
        bottom = top + self._device.height

        assert 0 <= left <= right <= self.width
        assert 0 <= top <= bottom <= self.height

        return (left, top, right, bottom)


class hotspot(mixin.capabilities):
    """
    A hotspot (`a place of more than usual interest, activity, or popularity`)
    is a live display which may be added to a virtual viewport - if the hotspot
    and the viewport are overlapping, then the :func:`update` method will be
    automatically invoked when the viewport is being refreshed or its position
    moved (such that an overlap occurs).

    You would either:

        * create a ``hotspot`` instance, suppling a render function (taking an
          :py:mod:`PIL.ImageDraw` object, ``width`` & ``height`` dimensions.
          The render function should draw within a bounding box of ``(0, 0,
          width, height)``, and render a full frame.

        * sub-class ``hotspot`` and override the :func:`should_redraw` and
          :func:`update` methods. This might be more useful for slow-changing
          values where it is not necessary to update every refresh cycle, or
          your implementation is stateful.
    """
    def __init__(self, width, height, draw_fn=None):
        self.capabilities(width, height, rotate=0)  # TODO: set mode?
        self._fn = draw_fn

    def paste_into(self, image, xy):
        im = Image.new(image.mode, self.size)
        draw = ImageDraw.Draw(im)
        self.update(draw)
        image.paste(im, xy)
        del draw

    def should_redraw(self):
        """
        Override this method to return true or false on some condition
        (possibly on last updated member variable) so that for slow changing
        hotspots they are not updated too frequently.
        """
        return True

    def update(self, draw):
        if self._fn:
            self._fn(draw, self.width, self.height)


class snapshot(hotspot):
    """
    A snapshot is a `type of` hotspot, but only updates once in a given
    interval, usually much less frequently than the viewport requests refresh
    updates.
    """
    def __init__(self, width, height, draw_fn=None, interval=1.0):
        assert interval > 0
        super(snapshot, self).__init__(width, height, draw_fn)
        self.interval = interval
        self.last_updated = -interval

    def should_redraw(self):
        """
        Only requests a redraw after ``interval`` seconds have elapsed.
        """
        return perf_counter() - self.last_updated > self.interval

    def paste_into(self, image, xy):
        super(snapshot, self).paste_into(image, xy)
        self.last_updated = perf_counter()


class terminal(object):
    """
    Provides a terminal-like interface to a device (or a device-like object
    that has :class:`mixin.capabilities` characteristics).
    """
    def __init__(self, device, font=None, color="white", bgcolor="black",
                 tabstop=4, line_height=None, animate=True, word_wrap=False):
        self._device = device
        self.font = font or ImageFont.load_default()
        self.default_fgcolor = color
        self.default_bgcolor = bgcolor
        self.animate = animate
        self.tabstop = tabstop
        self.word_wrap = word_wrap

        self._cw, self._ch = (0, 0)
        for i in range(32, 128):
            left, top, w, h = self.font.getbbox(chr(i))
            self._cw = max(w, self._cw)
            self._ch = max(h, self._ch)

        self._ch = line_height or self._ch
        self.width = device.width // self._cw
        self.height = device.height // self._ch
        self.size = (self.width, self.height)
        self.reset()
        self._backing_image = Image.new(self._device.mode, self._device.size,
            self._bgcolor)
        self._canvas = ImageDraw.Draw(self._backing_image)
        self.clear()

        if self.word_wrap:
            self.tw = TextWrapper()
            self.tw.width = self.width
            self.tw.expand_tabs = False
            self.tw.replace_whitespace = False
            self.tw.drop_whitespace = False
            self.tw.break_long_words = True

    def clear(self):
        """
        Clears the display and resets the cursor position to ``(0, 0)``.
        """
        self._cx, self._cy = (0, 0)
        self._canvas.rectangle(self._device.bounding_box,
                               fill=self.default_bgcolor)
        self.flush()

    def println(self, text=""):
        """
        Prints the supplied text to the device, scrolling where necessary.
        The text is always followed by a newline.

        :param text: The text to print.
        :type text: str
        """
        if self.word_wrap:
            # find directives in complete text
            directives = ansi_color.find_directives(text, self)

            # strip ansi from text
            clean_text = ansi_color.strip_ansi_codes(text)

            # wrap clean text
            clean_lines = self.tw.wrap(clean_text)

            # print wrapped text
            index = 0
            for line in clean_lines:
                line_length = len(line)
                y = 0
                while y < line_length:
                    method, args = directives[index]
                    if method == self.putch:
                        y += 1
                    method(*args)
                    index += 1
                self.newline()
        else:
            self.puts(text)
            self.newline()

    def puts(self, text):
        """
        Prints the supplied text, handling special character codes for carriage
        return (\\r), newline (\\n), backspace (\\b) and tab (\\t). ANSI color
        codes are also supported.

        If the ``animate`` flag was set to True (default), then each character
        is flushed to the device, giving the effect of 1970's teletype device.

        :param text: The text to print.
        :type text: str
        """
        for method, args in ansi_color.find_directives(text, self):
            method(*args)

    def putch(self, char):
        """
        Prints the specific character, which must be a valid printable ASCII
        value in the range 32..127 only, or one of carriage return (\\r),
        newline (\\n), backspace (\\b) or tab (\\t).

        :param char: The character to print.
        """
        if char == '\r':
            self.carriage_return()

        elif char == '\n':
            self.newline()

        elif char == '\b':
            self.backspace()

        elif char == '\t':
            self.tab()

        else:
            left, top, w, h = self.font.getbbox(char)
            if self._cx + w >= self._device.width:
                self.newline()

            self.erase()
            self._canvas.text((self._cx, self._cy),
                              text=char,
                              font=self.font,
                              fill=self._fgcolor)

            self._cx += w
            if self.animate:
                self.flush()

    def carriage_return(self):
        """
        Returns the cursor position to the left-hand side without advancing
        downwards.
        """
        self._cx = 0

    def tab(self):
        """
        Advances the cursor position to the next (soft) tabstop.
        """
        soft_tabs = self.tabstop - ((self._cx // self._cw) % self.tabstop)
        for _ in range(soft_tabs):
            self.putch(" ")

    def newline(self):
        """
        Advances the cursor position ot the left hand side, and to the next
        line. If the cursor is on the lowest line, the displayed contents are
        scrolled, causing the top line to be lost.
        """
        self.carriage_return()

        if self._cy + (2 * self._ch) >= self._device.height:
            # Simulate a vertical scroll
            copy = self._backing_image.crop((0, self._ch, self._device.width,
                self._device.height))
            self._backing_image.paste(copy, (0, 0))
            self._canvas.rectangle((0, copy.height, self._device.width,
                self._device.height), fill=self.default_bgcolor)
        else:
            self._cy += self._ch

        self.flush()
        if self.animate:
            sleep(0.2)

    def backspace(self):
        """
        Moves the cursor one place to the left, erasing the character at the
        current position. Cannot move beyond column zero, nor onto the
        previous line.
        """
        if self._cx + self._cw >= 0:
            self.erase()
            self._cx -= self._cw

        self.flush()

    def erase(self):
        """
        Erase the contents of the cursor's current position without moving the
        cursor's position.
        """
        bounds = (self._cx, self._cy, self._cx + self._cw, self._cy + self._ch)
        self._canvas.rectangle(bounds, fill=self._bgcolor)

    def flush(self):
        """
        Cause the current backing store to be rendered on the nominated device.
        """
        self._device.display(self._backing_image)

    def foreground_color(self, value):
        """
        Sets the foreground color.

        :param value: The new color value, either string name or RGB tuple.
        :type value: str or tuple
        """
        self._fgcolor = value

    def background_color(self, value):
        """
        Sets the background color.

        :param value: The new color value, either string name or RGB tuple.
        :type value: str or tuple
        """
        self._bgcolor = value

    def reset(self):
        """
        Resets the foreground and background color value back to the original
        when initialised.
        """
        self._fgcolor = self.default_fgcolor
        self._bgcolor = self.default_bgcolor

    def reverse_colors(self):
        """
        Flips the foreground and background colors.
        """
        self._bgcolor, self._fgcolor = self._fgcolor, self._bgcolor


class history(mixin.capabilities):
    """
    Wraps a device (or emulator) to provide a facility to be able to make a
    savepoint (a point at which the screen display can be "rolled-back" to).

    This is mostly useful for displaying transient error/dialog messages
    which could be subsequently dismissed, reverting back to the previous
    display.
    """
    def __init__(self, device):
        self.capabilities(device.width, device.height, rotate=0,
            mode=device.mode)
        if hasattr(device, "segment_mapper"):
            self.segment_mapper = device.segment_mapper
        self._savepoints = []
        self._device = device
        self._last_image = None

    def display(self, image):
        self._last_image = image.copy()
        self._device.display(image)

    def savepoint(self):
        """
        Copies the last displayed image.
        """
        if self._last_image:
            self._savepoints.append(self._last_image)
            self._last_image = None

    def restore(self, drop=0):
        """
        Restores the last savepoint. If ``drop`` is supplied and greater than
        zero, then that many savepoints are dropped, and the next savepoint is
        restored.

        :param drop:
        :type drop: int
        """
        assert drop >= 0
        while drop > 0:
            self._savepoints.pop()
            drop -= 1

        img = self._savepoints.pop()
        self.display(img)

    def __len__(self):
        """
        Indication of the number of savepoints retained.
        """
        return len(self._savepoints)


class sevensegment(object):
    """
    Abstraction that wraps a device, this class provides a ``text`` property
    which can be used to set and get a text value, which when combined with a
    ``segment_mapper`` sets the correct bit representation for seven-segment
    displays and propagates that onto the underlying device.

    :param device: A device instance.
    :param segment_mapper: An optional function that maps strings into the
        correct representation for the 7-segment physical layout. If not
        provided, the default mapper from compatible devices is used instead.
    :param undefined: The default character to substitute when an unrenderable
        character is supplied to the text property.
    :type undefined: char
    """
    def __init__(self, device, undefined="_", segment_mapper=None):
        self.device = device
        self.undefined = undefined
        self.segment_mapper = segment_mapper or device.segment_mapper
        self._bufsize = device.width * device.height // 8
        self.text = ""

    @property
    def text(self):
        """
        Returns the current state of the text buffer. This may not reflect
        accurately what is displayed on the seven-segment device, as certain
        alpha-numerics and most punctuation cannot be rendered on the limited
        display.
        """
        return self._text_buffer

    @text.setter
    def text(self, value):
        """
        Updates the seven-segment display with the given value. If there is not
        enough space to show the full text, an ``OverflowException`` is raised.

        :param value: The value to render onto the device. Any characters which
            cannot be rendered will be converted into the ``undefined``
            character supplied in the constructor.
        :type value: str
        """
        self._text_buffer = observable(mutable_string(value),
            observer=self._flush)

    def _flush(self, buf):
        data = bytearray(self.segment_mapper(buf, notfound=self.undefined)
            ).ljust(self._bufsize, b'\0')

        if len(data) > self._bufsize:
            raise OverflowError(
                f"Device's capabilities insufficient for value '{buf}'")

        with canvas(self.device) as draw:
            for x, byte in enumerate(reversed(data)):
                for y in range(8):
                    if byte & 0x01:
                        draw.point((x, y), fill="white")
                    byte >>= 1


class character(object):
    """
    Abstraction that wraps a device, this class provides a ``text`` property
    which can be used to set and get a text value allowing the device to be
    treated as a character style display such as the HD44780 LCD

    If the device is actually a character style device, be careful to provide
    a font that adheres to the pixel dimensions of the display.

    :param device: A device instance.
    :param font: The font to be used to paint the characters within the ``text``
        property.  If the device contains a font (e.g. hd44780, ws0010) it will
        be used as the default if no font is provided.
    :type font: `PIL.ImageFont` object
    :param undefined: The default character to substitute when an unrenderable
        character is supplied to the text property.
    :type undefined: char

    .. versionadded:: 1.15.0
    """

    def __init__(self, device, font=None, undefined="_"):
        self.device = device
        self._undefined = undefined

        self.font = font if font else device.font if hasattr(device, 'font') else None
        assert self.font, 'No font available'
        self.text = ''

    @property
    def text(self):
        """
        Returns the current state of the text buffer. This may not reflect
        accurately what is displayed on the device if the font does
        not have a symbol for a requested text value.
        """
        return self._text_buffer

    @text.setter
    def text(self, value):
        """
        Updates the display with the given value.

        :param value: The value to render onto the device. Any characters which
            cannot be rendered will be converted into the ``undefined``
            character supplied in the constructor. Newline characters '\n' work
            as expected but no other control characters (e.g. \r) are honored.
        :type value: str
        """
        self._text_buffer = observable(mutable_string(value),
            observer=self._flush)

    def _flush(self, buf):
        # Replace any characters that are not in the font with the undefined character
        buf = ''.join([i if i == '\n' or self.font.getlength(i) > 0 else self._undefined for i in buf])

        # Draw text onto display's image using the provided font
        with canvas(self.device) as draw:
            # Place text
            draw.text((0, 0), buf, fill='white', font=self.font, spacing=0)
