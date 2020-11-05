# -*- coding: utf-8 -*-
# Copyright (c) 2017-20 Richard Hull and contributors
# See LICENSE.rst for details.

import sys
if sys.version_info.major == 3:
    unicode = str


class mutable_string(object):

    def __init__(self, value):
        """
        Initialize the value.

        Args:
            self: (todo): write your description
            value: (todo): write your description
        """
        assert isinstance(value, str) or isinstance(value, unicode)
        self.target = value

    def __getattr__(self, attr):
        """
        Returns the value of an attribute

        Args:
            self: (todo): write your description
            attr: (str): write your description
        """
        return self.target.__getattribute__(attr)

    def __getitem__(self, key):
        """
        Return the value of key.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        return self.target[key]

    def __setitem__(self, key, value):
        """
        Sets the value of a list.

        Args:
            self: (todo): write your description
            key: (str): write your description
            value: (str): write your description
        """
        assert isinstance(value, str) or isinstance(value, unicode)
        tmp = list(self.target)
        tmp[key] = value
        self.target = ("" if isinstance(self.target, str) else u"").join(tmp)

    def __delitem__(self, key):
        """
        Remove an item from the list.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        tmp = list(self.target)
        del tmp[key]
        self.target = "".join(tmp)

    def __len__(self):
        """
        Returns the length of the iterator.

        Args:
            self: (todo): write your description
        """
        return len(self.target)

    def __iter__(self):
        """
        Returns an iterator over the iterator.

        Args:
            self: (todo): write your description
        """
        return iter(self.target)

    def __str__(self):
        """
        Return the string representation of this target.

        Args:
            self: (todo): write your description
        """
        return self.target

    def __repr__(self):
        """
        Return a repr representation of this object.

        Args:
            self: (todo): write your description
        """
        return repr(self.target)

    def __eq__(self, other):
        """
        Returns true if other objects are equal.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        if isinstance(self.target, unicode):
            return self.target == unicode(other)
        else:
            return self.target == str(other)

    def __hash__(self):
        """
        Returns the hash of the target.

        Args:
            self: (todo): write your description
        """
        return hash(self.target)


class observable(object):
    """
    Wraps any container object such that on inserting, updating or deleting,
    an observer is notified with a payload of the target. All other special
    name methods are passed through parameters unhindered.
    """
    def __init__(self, target, observer):
        """
        Initialize an observer.

        Args:
            self: (todo): write your description
            target: (todo): write your description
            observer: (todo): write your description
        """
        self.target = target
        self.observer = observer
        self.observer(self.target)

    def __getattr__(self, attr):
        """
        Returns the value of an attribute

        Args:
            self: (todo): write your description
            attr: (str): write your description
        """
        return self.target.__getattribute__(attr)

    def __getitem__(self, key):
        """
        Return the value of the key.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        return self.target.__getitem__(key)

    def __setitem__(self, key, value):
        """
        Set an item to key.

        Args:
            self: (todo): write your description
            key: (str): write your description
            value: (str): write your description
        """
        self.target.__setitem__(key, value)
        self.observer(self.target)

    def __delitem__(self, key):
        """
        Removes an item from the cache.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        self.target.__delitem__(key)
        self.observer(self.target)

    def __len__(self):
        """
        The number of the number of the iterator.

        Args:
            self: (todo): write your description
        """
        return self.target.__len__()

    def __iter__(self):
        """
        Return an iterator over the iterator.

        Args:
            self: (todo): write your description
        """
        return self.target.__iter__()

    def __str__(self):
        """
        Returns the string representation of this target.

        Args:
            self: (todo): write your description
        """
        return self.target.__str__()

    def __repr__(self):
        """
        Return the repr of this object.

        Args:
            self: (todo): write your description
        """
        return self.target.__repr__()


def from_16_to_8(data):
    """
    Utility function to take a list of 16 bit values and turn it into
    a list of 8 bit values

    :param data: list of 16 bit values to convert
    :type data: list
    :return: a list of 8 bit values
    :rtype: list

    .. versionadded:: 1.16.0
    """
    return [f(x) for x in data for f in (lambda x: (x & 0xFF00) >> 8, lambda x: 0xFF & x)]


def from_8_to_16(data):
    """
    Utility function to take a list of 8 bit values and turn it into a list
    of signed 16 bit integers

    :param data: list of 8 bit values to convert
    :type data: list
    :return: a list of 16 bit values
    :rtype: list

    .. versionadded:: 1.16.0
    """
    return [unsigned_16_to_signed(((data[i] & 0xFF) << 8) + (data[i + 1] & 0xFF))
        for i in range(0, len(data), 2)] if data is not None else None


def unsigned_16_to_signed(value):
    """
    Utility function to convert unsigned 16 bit value to a signed value

    :param value: the 16 bit value that needs to be converted
    :type value: int
    :return: a signed integer
    :rtype: int

    .. versionadded:: 1.16.0
    """
    return ((value) & 0x7FFF) - (0x8000 & (value))


def bytes_to_nibbles(data):
    """
    Utility function to take a list of bytes (8 bit values) and turn it into
    a list of nibbles (4 bit values)

    :param data: a list of 8 bit values that will be converted
    :type data: list
    :return: a list of 4 bit values
    :rtype: list

    .. versionadded:: 1.16.0
    """
    return [f(x) for x in data for f in (lambda x: x >> 4, lambda x: 0x0F & x)]
