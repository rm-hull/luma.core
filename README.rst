luma.core **|** 
`luma.docs <https://github.com/rm-hull/luma.docs>`__ **|** 
`luma.emulator <https://github.com/rm-hull/luma.emulator>`__ **|** 
`luma.examples <https://github.com/rm-hull/luma.examples>`__ **|** 
`luma.lcd <https://github.com/rm-hull/luma.lcd>`__ **|** 
`luma.led_matrix <https://github.com/rm-hull/luma.led_matrix>`__ **|** 
`luma.oled <https://github.com/rm-hull/luma.oled>`__ 

luma.core
=========

.. image:: https://travis-ci.org/rm-hull/luma.core.svg?branch=master
   :target: https://travis-ci.org/rm-hull/luma.core

.. image:: https://coveralls.io/repos/github/rm-hull/luma.core/badge.svg?branch=master
   :target: https://coveralls.io/github/rm-hull/luma.core?branch=master

.. image:: https://img.shields.io/pypi/pyversions/luma.core.svg
   :target: https://pypi.python.org/pypi/luma.core

.. image:: https://img.shields.io/pypi/v/luma.core.svg
   :target: https://pypi.python.org/pypi/luma.core

.. image:: https://img.shields.io/maintenance/yes/2020.svg?maxAge=2592000

**luma.core** is a component library providing a `Pillow <https://pillow.readthedocs.io/>`_-compatible
drawing canvas for Python 3, and other functionality to support drawing primitives and
text-rendering capabilities for small displays on the Raspberry Pi and other
single board computers:

* scrolling/panning capability,
* terminal-style printing,
* state management,
* color/greyscale (where supported),
* dithering to monochrome,
* sprite animation,
* flexible framebuffering (depending on device capabilities)

Documentation
-------------

API documentation can be found at https://luma-core.readthedocs.io/en/latest/

Drivers
-------

Device drivers extend **luma.core** to provide the correct initialization
sequences for specific physical display devices/chipsets.

There are several drivers for different classes of device available:

* `luma.oled <https://github.com/rm-hull/luma.oled/>`_
* `luma.lcd <https://github.com/rm-hull/luma.lcd/>`_
* `luma.led_matrix <https://github.com/rm-hull/luma.led_matrix/>`_
* `luma.emulator <https://github.com/rm-hull/luma.emulator/>`_

Emulators
---------

There are emulators that run in real-time (with pygame) and others that can
take screenshots, or assemble animated GIFs, as per the examples below. Source
code for these are available in the `examples
<https://github.com/rm-hull/luma.examples/tree/master/examples>`_
directory of the ``luma.examples`` repository.

.. image:: https://raw.githubusercontent.com/rm-hull/luma.oled/master/doc/images/clock_anim.gif?raw=true
   :alt: clock

.. image:: https://raw.githubusercontent.com/rm-hull/luma.oled/master/doc/images/invaders_anim.gif?raw=true
   :alt: invaders

.. image:: https://raw.githubusercontent.com/rm-hull/luma.oled/master/doc/images/crawl_anim.gif?raw=true
   :alt: crawl

License
-------
The MIT License (MIT)

Copyright (c) 2017-2020 Richard Hull and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
