ChangeLog
---------

+------------+---------------------------------------------------------------------+------------+
| Version    | Description                                                         | Date       |
+============+=====================================================================+============+
| **0.9.2**  | * Add ``background=`` option to ``luma.core.render.canvas``         | 2017/06/19 |
|            | * Add TCA9548A I2C multiplex scanner (contrib)                      |            |
|            | * Display I2C address in hex when error occurs                      |            |
+------------+---------------------------------------------------------------------+------------+
| **0.9.1**  | * Add cmdline block orientation of 180                              | 2017/05/01 |
+------------+---------------------------------------------------------------------+------------+
| **0.9.0**  | * Add word-wrap capability to ``luma.core.virtual.terminal``        | 2017/04/22 |
|            | * Bug fix to ``luma.core.virtual.terminal`` when scrolling          |            |
+------------+---------------------------------------------------------------------+------------+
| **0.8.1**  | * Propagate segment_mapper through other virtual devices            | 2017/04/14 |
+------------+---------------------------------------------------------------------+------------+
| **0.8.0**  | * Migrate seven-segment wrapper from ``luma.led_matrix``            | 2017/04/14 |
+------------+---------------------------------------------------------------------+------------+
| **0.7.5**  | * Allow alternative RPi.GPIO implementations                        | 2017/04/09 |
+------------+---------------------------------------------------------------------+------------+
| **0.7.4**  | * Reduce size of space character in legacy proportional font        | 2017/04/09 |
+------------+---------------------------------------------------------------------+------------+
| **0.7.3**  | * Cmdline args now supports backlight active high/low               | 2017/04/07 |
+------------+---------------------------------------------------------------------+------------+
| **0.7.2**  | * Add ``--h-offset=N`` and ``--v-offset=N`` params to cmdline args  | 2017/04/07 |
+------------+---------------------------------------------------------------------+------------+
| **0.7.1**  | * Improve formatting in command line options                        | 2017/04/06 |
+------------+---------------------------------------------------------------------+------------+
| **0.7.0**  | * Add software-based bitbang SPI implementation                     | 2017/03/27 |
|            | * Cmdline args parsing                                              |            |
|            | * Use monotonic clock                                               |            |
+------------+---------------------------------------------------------------------+------------+
| **0.6.2**  | * Move GPIO.setmode() to point when referenced                      | 2017/03/19 |
|            | * Use regex prefix in ANSI color parser (fixes deprecation warning) |            |
+------------+---------------------------------------------------------------------+------------+
| **0.6.1**  | * Deprecate spi params                                              | 2017/03/13 |
|            | * Fix resource leak in spritesheet                                  |            |
+------------+---------------------------------------------------------------------+------------+
| **0.6.0**  | * Terminal supports ANSI Color escape codes                         | 2017/03/13 |
|            | * Catch & rethrow IOErrors                                          |            |
+------------+---------------------------------------------------------------------+------------+
| **0.5.4**  | * Rework decorators                                                 | 2017/03/08 |
+------------+---------------------------------------------------------------------+------------+
| **0.5.3**  | * Catch & rethrow all RPi.GPIO RuntimeExceptions                    | 2017/03/08 |
+------------+---------------------------------------------------------------------+------------+
| **0.5.2**  | * Raise ``error.UnsupportedPlatform`` if RPi.GPIO is not available  | 2017/03/08 |
|            | * Bug fix to ``luma.core.virtual.terminal`` to handle multiple \\n  |            |
+------------+---------------------------------------------------------------------+------------+
| **0.5.1**  | * Bug fix: ``legacy.show_message`` regression                       | 2017/03/05 |
+------------+---------------------------------------------------------------------+------------+
| **0.5.0**  | * **BREAKING CHANGES:** Rework ``framework_regulator`` class        | 2017/03/05 |
|            | * Documentation updates                                             |            |
+------------+---------------------------------------------------------------------+------------+
| **0.4.4**  | * Bug fix: ``legacy.show_message`` off-by-one bug                   | 2017/03/02 |
+------------+---------------------------------------------------------------------+------------+
| **0.4.3**  | * Restrict exported Python symbols from ``luma.core.serial``        | 2017/03/02 |
+------------+---------------------------------------------------------------------+------------+
| **0.4.2**  | * Optional alignment of framebuffer bounding_box to word-boundaries | 2017/02/28 |
+------------+---------------------------------------------------------------------+------------+
| **0.4.1**  | * Refactor framebuffer interface                                    | 2017/02/27 |
+------------+---------------------------------------------------------------------+------------+
| **0.4.0**  | * Add spritesheet and framerate_regulator functionality             | 2017/02/27 |
|            | * Add full-frame and diff-to-previous framebuffer implementations   |            |
|            | * Remove unnecessary travis/tox dependencies                        |            |
+------------+---------------------------------------------------------------------+------------+
| **0.3.2**  | * Bug fix: ``legacy.show_message`` wrong device height              | 2017/02/24 |
|            | * Add Cyrillic chars to legacy font                                 |            |
|            | * Make pytest-runner a conditional requirement                      |            |
+------------+---------------------------------------------------------------------+------------+
| **0.3.1**  | * Imported legacy font handling from ``rm-hull/luma.led_matrix``    | 2017/02/19 |
+------------+---------------------------------------------------------------------+------------+
| **0.2.0**  | * Fix bug in seven_segment transform (display correct char)         | 2017/02/17 |
|            | * Moved emulator code to ``rm-hull/luma.emulator`` github repo      |            |
+------------+---------------------------------------------------------------------+------------+
| **0.1.15** | * Require at least Pillow 4.0.0                                     | 2017/02/11 |
|            | * Configurable ``transfer_size`` on SPI writes                      |            |
|            | * Documentation updates                                             |            |
+------------+---------------------------------------------------------------------+------------+
| **0.1.14** | * Use a more flexible no-op implementation                          | 2017/02/03 |
|            | * Use spidev's ``writebytes()`` rather than ``xfer2()``             |            |
|            | * Dont write GIF animation if nothing was displayed                 |            |
|            | * Attempt to optimize palette when saving GIF animations            |            |
+------------+---------------------------------------------------------------------+------------+
| **0.1.13** | * Fix bug in setup script                                           | 2017/01/23 |
+------------+---------------------------------------------------------------------+------------+
| **0.1.12** | * Assert valid SPI bus speed                                        | 2017/01/21 |
|            | * Don't report errors in shutdown                                   |            |
|            | * Don't package as zip-safe                                         |            |
|            | * Add 7-segment LED emulation transformer                           |            |
+------------+---------------------------------------------------------------------+------------+
| **0.1.11** | * Rejig packaging to include emulator assets                        | 2017/01/20 |
+------------+---------------------------------------------------------------------+------------+
| **0.1.3**  | * Reset SPI device on initialization                                | 2017/01/19 |
|            | * Add LED matrix emulation transformer                              |            |
+------------+---------------------------------------------------------------------+------------+
| **0.1.2**  | * Namespace packaging                                               | 2017/01/10 |
+------------+---------------------------------------------------------------------+------------+
| **0.1.0**  | * Split out core functionality from ``rm-hull/ssd1306``             | 2017/01/10 |
+------------+---------------------------------------------------------------------+------------+
