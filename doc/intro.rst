Introduction
------------
**luma.core** is a component library providing a Pillow-compatible drawing
canvas, and other functionality to support drawing primitives and
text-rendering capabilities for small displays on the Raspberry Pi and other
single board computers:

* scrolling/panning capability,
* terminal-style printing,
* state management,
* color/greyscale (where supported),
* dithering to monochrome,
* sprite animation,
* flexible framebuffering (depending on device capabilities)

Device drivers extend **luma.core** to provide the correct initialization
sequences for specific physical display devices/chipsets.

There are several drivers for different classes of device available:

* `luma.oled <https://github.com/rm-hull/luma.oled/>`_
* `luma.lcd <https://github.com/rm-hull/luma.lcd/>`_
* `luma.led_matrix <https://github.com/rm-hull/luma.led_matrix/>`_

There are emulators that run in real-time (with pygame) and others that can
take screenshots, or assemble animated GIFs, as per the examples below (source
code for these is available in the `luma.examples
<https://github.com/rm-hull/luma.examples/tree/master/examples>`_ directory:

.. image:: https://raw.githubusercontent.com/rm-hull/luma.oled/master/doc/images/clock_anim.gif?raw=true
   :alt: clock

.. image:: https://raw.githubusercontent.com/rm-hull/luma.oled/master/doc/images/invaders_anim.gif?raw=true
   :alt: invaders

.. image:: https://raw.githubusercontent.com/rm-hull/luma.oled/master/doc/images/crawl_anim.gif?raw=true
   :alt: crawl


