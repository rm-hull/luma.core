#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.


from luma.core.util import observable, mutable_string


class test_bell(object):

    called = 0

    def ding(self, *args):
        """
        Set the current position.

        Args:
            self: (todo): write your description
        """
        self.called += 1


def test_length():
    """
    Calculate the length of the test.

    Args:
    """
    bell = test_bell()
    buf = observable(bytearray("hello", "utf-8"), bell.ding)
    assert len(buf) == 5
    assert bell.called == 1


def test_iteration():
    """
    Iterate an iteration of an iteration.

    Args:
    """
    bell = test_bell()
    buf = observable(bytearray("hello", "utf-8"), bell.ding)
    assert list(iter(buf)) == [ord(ch) for ch in "hello"]
    assert bell.called == 1


def test_getattribute():
    """
    Get an attribute of an attribute.

    Args:
    """
    bell = test_bell()
    buf = observable(bytearray("hello", "utf-8"), bell.ding)
    assert list(iter(buf.decode("utf-8"))) == list("hello")
    assert bell.called == 1


def test_getitem():
    """
    Return the test test.

    Args:
    """
    bell = test_bell()
    buf = observable(mutable_string("hello"), bell.ding)
    assert buf[2] == "l"
    assert bell.called == 1


def test_setitem():
    """
    Sets the test setitem.

    Args:
    """
    bell = test_bell()
    buf = observable(mutable_string("hello"), bell.ding)
    buf[0] = "y"
    assert str(buf) == "yello"
    assert bell.called == 2


def test_setslice():
    """
    Determine the test sets.

    Args:
    """
    bell = test_bell()
    buf = observable(mutable_string("hello"), bell.ding)
    buf[1:4] = "ipp"
    assert str(buf) == "hippo"
    assert bell.called == 2


def test_delitem():
    """
    Delete a test test.

    Args:
    """
    bell = test_bell()
    buf = observable(mutable_string("hello"), bell.ding)
    del buf[4]
    assert str(buf) == "hell"
    assert bell.called == 2


def test_getslice():
    """
    Set the test islice.

    Args:
    """
    bell = test_bell()
    buf = observable(mutable_string("hello"), bell.ding)
    assert buf[2:4] == "ll"
    assert bell.called == 1


def test_repr():
    """
    Print the test test.

    Args:
    """
    bell = test_bell()
    buf = observable(bytearray("hello", "utf-8"), bell.ding)
    assert repr(buf) == "bytearray(b'hello')"
    assert bell.called == 1
