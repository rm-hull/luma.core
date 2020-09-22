# -*- coding: utf-8 -*-
# Copyright (c) 2020 Richard Hull and contributors
# See LICENSE.rst for details.

from pathlib import Path
from math import ceil
from copy import deepcopy
from PIL import Image, ImageFont
import cbor2
from luma.core.util import from_16_to_8, from_8_to_16


class bitmap_font():
    """
    An PIL.Imagefont style font

    The structure of this class was modeled after the PIL ImageFont class
    and is intended to be interchangable for PIL.ImageFont objects.  It has
    the following additional capabilities.

    * Allows fonts larger than 256 characters to be created
    * Font can be combined with other fonts
    * Font characters can be mapped to their correct unicode codepoints
    * Font can be initialized from a basic sprite table (with conditions)

    .. note:
        Because this font is implemented completely in Python it will be slower
        than a native PIL.ImageFont object.

    .. versionadded:: 1.16.0
    """

    PUA_SPACE = 0xF8000

    def __init__(self):
        self.mappings = {}
        self.metrics = []

    def load(self, filename):
        """
        Load font from filename

        :param filename: the filename of the file containing the font data
        :type filename: str
        :return: a font object
        :rtype: luma.core.bitmap_font
        """
        with open(filename, 'rb') as fp:
            s = fp.readline()
            if s != b'LUMA.CORE.BITMAP_FONT\n':
                raise SyntaxError('Not a luma.core.bitmap_font file')
            fontdata = cbor2.load(fp)

        self._load_fontdata(fontdata)
        return self

    def loads(self, fontdata):
        """
        Load luma.core.bitmap_font from a string of serialized data produced
        by the dumps method

        :param fontdata: The serialized font data that will be used to initialize
            the font.  This data is produced by the luma.core.bitmap_font.dumps
            method.
        :type fontdata: bytes
        :return: a font object
        :rtype: luma.core.bitmap_font
        """
        fontdata = cbor2.loads(fontdata)
        self._load_fontdata(fontdata)
        return self

    def load_pillow_font(self, file, mappings=None):
        """
        Create luma.core.bitmap_font from a PIL ImageFont style font.

        :param file: The filename of the PIL.ImageFont to load
        :type file: str
        :param mappings: a dictionary of unicode to value pairs (optional).
            Mappings allow the appropriate unicode values to be provided for
            each character contained within the font
        :type mappings: dict
        :return: a font object
        :rtype: luma.core.bitmap_font
        """
        with open(file, 'rb') as fp:
            if fp.readline() != b"PILfont\n":
                raise SyntaxError("Not a PIL.ImageFont file")
            while True:
                s = fp.readline()
                if not s:
                    raise SyntaxError("PIL.ImageFont file missing metric data")
                if s == b"DATA\n":
                    break
            data = fp.read(256 * 20)
            if len(data) != 256 * 20:
                raise SyntaxError("PIL.ImageFont file metric data incomplete")

        sprite_table = self._get_image(file)
        self._populate_metrics(sprite_table, data, range(256), mappings)
        sprite_table.close()
        return self

    def load_sprite_table(self, sprite_table, index, xwidth, glyph_size, cell_size, mappings=None):
        """
        Load a font from a sprite table

        :param sprite_table: A PIL.Image representation of every glyph within the font
        :type sprite_table: PIL.Image
        :param index: The list of character values contained within sprite_table.
            This list MUST be in the same order that the glyphs for the characters
            appear within the sprite_table (in left to right, top to bottom order)
        :type index: list or other iterable
        :param xwidth: number of pixels between placements of each character in a
            line of text
        :type xwidth: int
        :param glyph_size: tuple containing the width and height of each character
            in the font
        :type glyph_size: tuple(int, int)
        :param cell_size: tuple containing the width and height of each cell in the
            sprite table.  Defaults to the size of the glyphs.
        :type cell_size: tuple(int, int)
        :param mappings: a dictionary of unicode to value pairs (optional)
            Mappings allow the appropriate unicode values to be provided for
            each character contained within the font
        :type mappings: dict
        :return: a font object
        :rtype: luma.core.bitmap_font

        .. note:
            Font contained within table must adhere to the following conditions
            * All glyphs must be the same size
            * Glyphs are contained within the sprite table in a grid arrangement
            * The grid is filled with glyphs placed in horizontal order
            * Each cell in the grid is the same size
            * The placement of each glyph has no offset from its origin
        """

        table_width = sprite_table.size[0]

        # Each character uses the same data
        line = [xwidth, 0, 0, -glyph_size[1], glyph_size[0], 0]

        data = []
        # Generate an entry for each character
        for c in range(len(index)):
            offset = c * cell_size[0]
            left = offset % table_width
            top = (offset // table_width) * cell_size[1]
            right = left + glyph_size[0]
            bottom = top + glyph_size[1]
            data = data + line + [left, top, right, bottom]
        self._populate_metrics(sprite_table, from_16_to_8(data), index, mappings)
        return self

    def save(self, filename):
        """
        Write luma.core.bitmap_font data to a file
        """
        with open(filename, 'wb') as fp:
            fontdata = self._generate_fontdata()
            fp.write(b'LUMA.CORE.BITMAP_FONT\n')
            cbor2.dump(fontdata, fp)

    def dumps(self):
        """
        Serializes the font data for transfer or storage

        :return: serialized font data
        :rtype: bytes
        """
        fontdata = self._generate_fontdata()
        return cbor2.dumps(fontdata)

    def _generate_fontdata(self):
        """
        Utility method to create an efficient serializable representation
        of a luma.core.bitmap_font
        """
        cell_size = (self.width, self.height)

        area = self.count * self.width * self.height
        table_width = ((ceil(area**0.5) + self.width - 1) // self.width) * self.width
        table_height = ((ceil(area / table_width) + self.height - 1) // self.height) * self.height

        image = Image.new('1', (table_width, table_height))
        metrics = []
        for i, v in enumerate(self.metrics):
            offset = i * cell_size[0]
            left = offset % table_width
            top = (offset // table_width) * cell_size[1]
            image.paste(v['img'], (left, top))
            metrics.append((v['xwidth'], v['dst']))

        fontdata = {}
        fontdata['type'] = 'LUMA.CORE.BITMAP_FONT'
        fontdata['count'] = len(self.metrics)
        if self.regular:
            fontdata['xwidth'] = self.regular[0]
            fontdata['glyph_size'] = (self.width, self.height)
        fontdata['cell_size'] = cell_size
        fontdata['mappings'] = self.mappings
        fontdata['sprite_table_dimensions'] = (table_width, table_height)
        fontdata['sprite_table'] = image.tobytes()
        if not self.regular:
            fontdata['metrics'] = metrics

        return fontdata

    def _load_fontdata(self, fontdata):
        """
        Initialize font from deserialized data
        """
        try:
            count = fontdata['count']
            xwidth = fontdata.get('xwidth')
            glyph_size = fontdata.get('glyph_size')
            cell_size = fontdata['cell_size']
            self.mappings = fontdata['mappings']
            table_width, table_height = fontdata['sprite_table_dimensions']
            image = Image.frombytes('1', (table_width, table_height), fontdata['sprite_table'])
            metrics = fontdata.get('metrics')
        except (KeyError, TypeError, ValueError):
            raise ValueError('Cannot parse fontdata. It is invalid.')

        self.metrics = []
        for i in range(count):
            offset = i * cell_size[0]
            metric = metrics[i] if metrics else (xwidth, [0, -glyph_size[1], glyph_size[0], 0])
            left = offset % table_width
            top = (offset // table_width) * cell_size[1]
            right = left + (metric[1][2] - metric[1][0])
            bottom = top + (metric[1][3] - metric[1][1])

            self.metrics.append({
                'xwidth': metric[0],
                'dst': metric[1],
                'img': image.crop((left, top, right, bottom))
            })
        self._calculate_font_size()

    def _get_image(self, filename):
        """
        Load sprite_table associated with font
        """
        ifs = {p.resolve() for p in Path(filename).parent.glob(Path(filename).stem + ".*") if p.suffix in (".png", ".gif", ".pbm")}
        for f in ifs:
            try:
                image = Image.open(f)
            except:
                pass
            else:
                if image.mode in ['1', 'L']:
                    break
                image.close()
        else:
            raise OSError('cannot find glyph data file')
        return image

    def _lookup(self, val):
        """
        Utility method to determine a characters placement within the metrics list
        """
        if val in self.mappings:
            return self.mappings[val]
        if val + self.PUA_SPACE in self.mappings:
            return self.mappings[val + self.PUA_SPACE]
        return None

    def _getsize(self, text):
        """
        Utility method to compute the rendered size of a line of text.  It
        also computes the minimum column value for the line of text. This is
        needed in case the font has a negative horizontal offset which
        requires that the size be expanded to accomodate the extra pixels.
        """
        min_col = max_col = cp = 0
        for c in text:
            m = self._lookup(ord(c))
            if m is None:
                # Ignore characters that do not exist in font
                continue
            char = self.metrics[m]
            min_col = min(min_col, char['dst'][0] + cp)
            max_col = max(max_col, char['dst'][2] + cp)
            cp += char['xwidth']
        return (max_col - min_col, self.height, min_col)

    def getsize(self, text, *args, **kwargs):
        """
        Wrapper for _getsize to match the interface of PIL.ImageFont
        """
        width, height, min = self._getsize(text)
        return (width, height)

    def getmask(self, text, mode="1", *args, **kwargs):
        """
        Implements an PIL.ImageFont compatible method to return the rendered
        image of a line of text
        """

        # TODO: Test for potential character overwrite if horizontal offset is < 0
        assert mode in ['1', 'L']
        width, height, min = self._getsize(text)
        image = Image.new(mode, (width, height))

        # Adjust start if any glyph is placed before origin
        cp = -min if min < 0 else 0

        for c in text:
            m = self._lookup(ord(c))
            if m is None:
                # Ignore characters that do not exist in font
                continue
            char = self.metrics[m]
            px = char['dst'][0] + cp
            py = char['dst'][1] + self.baseline
            image.paste(char['img'], (px, py))
            cp += char['xwidth']
        return image.im

    def _populate_metrics(self, sprite_table, data, index, mappings):
        """
        Populate metrics on initial font load from a sprite table or PIL ImageFont
        Place characters contained on the sprite_table into Unicode
        private use area (PUA).  Create a reverse lookup from the values
        that are contained on the sprite_table.

        .. note:
            Arbritarily using Supplemental Private Use Area-A starting at
            PUA_SPACE (0xF8000) to give the raw sprite_table locations
            a unicode codepoint.
        """

        self.metrics = []
        self.glyph_index = {}
        self.data = data
        idx = 0

        rev_map = {}
        if mappings is not None:
            for k, v in mappings.items():
                if v in rev_map:
                    rev_map[v].append(k)
                else:
                    rev_map[v] = [k]

        self.mappings = {}
        for i, c in enumerate(index):
            metric = from_8_to_16(data[i * 20:(i + 1) * 20])

            # If character position has no data, skip it
            if sum(metric) == 0:
                continue

            xwidth = metric[0]
            dst = metric[2:6]
            src = metric[6:10]

            img = sprite_table.crop((src[0], src[1], src[2], src[3]))
            self.metrics.append({
                'xwidth': xwidth,
                'dst': dst,
                'img': img
            })
            self.mappings[c + self.PUA_SPACE] = idx
            if c in rev_map:
                for u in rev_map[c]:
                    self.mappings[u] = idx
            i2b = img.tobytes()
            # Only add new glyphs except always add space character
            if i2b not in self.glyph_index or c == 0x20:
                self.glyph_index[i2b] = c
            idx += 1

        self._calculate_font_size()

    def _calculate_font_size(self):
        # Calculate height and baseline of font
        ascent = descent = width = 0

        m = self.metrics[0]
        regular = (m['xwidth'], m['dst'])
        xwidth = regular[0]
        regular_flag = True
        for m in self.metrics:
            if regular != (m['xwidth'], m['dst']):
                regular_flag = False
            ascent = max(ascent, -m['dst'][1])
            descent = max(descent, m['dst'][3])
            width = max(width, m['dst'][2] - m['dst'][0])
            xwidth = max(xwidth, m['xwidth'])
        self.height = ascent + descent
        self.width = width
        self.baseline = ascent
        self.regular = regular if regular_flag else None
        self.count = len(self.metrics)

    def combine(self, source_font, characters=None, force=False):
        """
        Combine two luma.core.bitmap_fonts

        :param source_font: a luma.core.bitmap_font to copy from
        :type: luma.core.bitmap_font
        :param characters: (optional) A list of the characters to transfer from
            the source_font.  If not provided, all of the characters within
            the source_font will be transferred.
        :type characters: str
        :param force: If set, the source_font can overwrite values that already
            exists within this font.  Default is False.
        :type force: bool
        """

        if characters:
            for c in characters:
                if ord(c) in self.mappings and not force:
                    continue
                m = source_font._lookup(ord(c))
                if m is not None:
                    v = source_font.metrics[m]
                else:
                    raise ValueError('{0} is not a valid character within the source font'.format(c))
                self.metrics.append(v)
                self.mappings[ord(c)] = len(self.metrics) - 1
        else:
            # Copy source values into destination but don't overwrite existing characters unless force set
            for k, v in source_font.mappings.items():
                if k in self.mappings and not force:
                    continue
                self.metrics.append(source_font.metrics[v])
                self.mappings[k] = len(self.metrics) - 1

        # Recompute font size metrics
        self._calculate_font_size()


def load(filename):
    """
    Load a luma.core.bitmap_font file.  This function creates a
    luma.core.bitmap_font object from the given luma.core.bitmap_font file, and
    returns the corresponding font object.

    :param filename: Filename of font file.
    :type filename: str
    :return: A luma.core.bitmap_font object.
    :exception OSError: If the file could not be read.
    :exception SyntaxError: If the file does not contain the expected data
    """
    f = bitmap_font()
    f.load(filename)
    return f


def loads(data):
    """
    Load a luma.core.bitmap_font from a string of serialized data.  This function
    creates a luma.core.bitmap object from serialized data produced from the
    dumps method and returns the corresponding font object.

    :param data: Serialized luma.core.bitmap_font data.
    :type data: str
    :return: A luma.core.bitmap_font object.
    :exception ValueError: If the data does not a valid luma.core.bitmap_font
    """
    f = bitmap_font()
    f.loads(data)
    return f


def load_pillow_font(filename, mappings=None):
    """
    Load a PIL font file.  This function creates a luma.core.bitmap_font object
    from the given PIL bitmap font file, and returns the corresponding font object.

    :param filename: Filename of font file.
    :type filename: str
    :param mappings: a dictionary of unicode to value pairs (optional)
    :type mappings: dict
    :return: A font object.
    :exception OSError: If the file could not be read.
    :exception SyntaxError: If the file does not contain the expected data
    """
    f = bitmap_font()
    f.load_pillow_font(filename, mappings)
    return f


def load_sprite_table(sprite_table, index, xwidth, glyph_size, cell_size=None, mappings=None):
    """
    Create a luma.core.bitmap_font from a sprite table.

    :param sprite_table: Filename of a sprite_table file or a PIL.Image containing the
        sprite_table
    :type sprite_table: str or PIL.Image
    :param index: The list of character values contained within sprite_table.
        This list MUST be in the same order that the glyphs for the characters
        appear within the sprite_table (in left to right, top to bottom order)
    :type index: list or other iterable
    :param xwidth: number of pixels between placements of each character in a
        line of text
    :type xwidth: int
    :param glyph_size: tuple containing the width and height of each character
        in the font
    :type glyph_size: tuple(int, int)
    :param cell_size: tuple containing the width and height of each cell in the
        sprite table.  Defaults to the size of the glyphs.
    :type cell_size: tuple(int, int)
    :param mappings: a dictionary of unicode to value pairs (optional)
    :type mappings: dict
    :return: A font object.
    :exception OSError: If the file could not be read.
    :exception SyntaxError: If the file does not contain the expected data

    .. note:
        Requires a font where each character is the same size with no horizontal
        or vertical offset and has consistant horizontal distance between each
        character
    """
    f = bitmap_font()
    need_to_close = False
    if type(sprite_table) == str:
        try:
            sprite_table = Image.open(sprite_table)
            need_to_close = True
        # Differentiate between file not found and invalid sprite table
        except FileNotFoundError:
            raise
        except IOError:
            raise ValueError('File {0} not a valid sprite table'.format(sprite_table))

    if isinstance(sprite_table, Image.Image):
        cell_size = cell_size if cell_size is not None else glyph_size
        f.load_sprite_table(sprite_table, index, xwidth, glyph_size, cell_size, mappings)
    else:
        raise ValueError('Provided image is not an instance of PIL.Image')

    if need_to_close:
        sprite_table.close()
    return f


class embedded_fonts(ImageFont.ImageFont):
    """
    Utility class to manage the set of fonts that are embedded within a
    compatible device.

    :param data: The font data from the device.  See note below.
    :type data: dict
    :param selected_font: The font that should be loaded as this device's
        default.  Will accept the font's index or its name.
    :type selected_font: str or int

    ..note:
        The class is used by devices which have embedded fonts and is not intended
        to be used directly. To initialize it requires providing a dictionary
        of font data including a `PIL.Image.tobytes` representation of a
        sprite_table which contains the glyphs of the font organized in
        consistent rows and columns, a metrics dictionary which provides the
        information on how to retrieve fonts from the sprite_table, and a
        mappings dictionary that provides unicode to table mappings.

    .. versionadded:: 1.16.0
    """
    def __init__(self, data, selected_font=0):
        self.data = data
        self.font_by_number = {}
        self.names_index = {}

        for i in range(len(data['metrics'])):
            name = data['metrics'][i]['name']
            self.names_index[name] = i

        self.current = selected_font

    def load(self, val):
        """
        Load a font by its index value or name and return it

        :param val: The index or the name of the font to return
        :type val: int or str
        """
        if type(val) is str:
            if val in self.names_index:
                index = self.names_index[val]
            else:
                raise ValueError('No font with name {0}'.format(val))
        elif type(val) is int:
            if val in range(len(self.names_index)):
                index = val
            else:
                raise ValueError('No font with index {0}'.format(val))
        else:
            raise TypeError('Expected int or str.  Received {0}'.format(type(val)))

        if index not in self.font_by_number:
            i = index
            index_list = self.data['metrics'][i]['index']
            xwidth = self.data['metrics'][i]['xwidth']
            cell_size = self.data['metrics'][i]['cell_size']
            glyph_size = self.data['metrics'][i]['glyph_size']
            table_size = self.data['metrics'][i]['table_size']
            mappings = self.data['mappings'][i] if 'mappings' in self.data else None
            sprite_table = Image.frombytes('1', table_size, self.data['fonts'][i])
            font = load_sprite_table(sprite_table, index_list, xwidth, glyph_size, cell_size, mappings)
            self.font_by_number[i] = font

        return self.font_by_number[index]

    @property
    def current(self):
        """
        Returns the currently selected font
        """
        return self.font

    @current.setter
    def current(self, val):
        """
        Sets the current font, loading the font if it has not previously been selected

        :param val:  The name or index number of the selected font.
        :type val: str or int
        """
        self.font = self.load(val)

    def combine(self, font, characters=None, force=False):
        """
        Combine the current font with a new one

        :param font: The font to combine with the current font
        :type font: luma.core.bitmap
        :param characters: (Optional) A list of characters to move from the new font to the
            current font.  If not provided all characters from the new font will
            be transferred.
        :type characters: list of unicode characters
        :param force: Determines if conflicting characters should be ignored (default)
            or overwritten.

        .. note:
          This does not permanently change the embedded font.  If you set the value
          of current again even if setting it to the same font, the changes that combine
          has made will be lost.
        """
        destination = deepcopy(self.font)
        destination.combine(font, characters, force)
        self.font = destination
