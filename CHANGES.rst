ChangeLog
---------

+------------+---------------------------------------------------------------------+------------+
| Version    | Description                                                         | Date       |
+============+=====================================================================+============+
| **2.0.2**  | * Change order of namepaces cmdline, so SSD1306 is default          | 2020/11/26 |
+------------+---------------------------------------------------------------------+------------+
| **2.0.1**  | * Fix to allow cmdline args to dynamically create a full_frame()    | 2020/11/06 |
|            |   instance                                                          |            |
+------------+---------------------------------------------------------------------+------------+
| **2.0.0**  | * Improved diff_to_previous framebuffer performance                 | 2020/11/02 |
|            | * Add Linux framebuffer pseudo-device                               |            |
|            | * Allow a wider range of SPI bus speeds                             |            |
+------------+---------------------------------------------------------------------+------------+
| **1.17.3** | * Drop support for Python 3.5, only 3.6 or newer is supported now   | 2020/10/24 |
|            | * Add missing cmdline interfaces: "noop" & "gpio_cs_spi"            |            |
|            | * Legacy proportional font wrapper raises user-friendly error       |            |
|            |   message when character is not in the font table                   |            |
+------------+---------------------------------------------------------------------+------------+
| **1.17.2** | * Remove SPI cs_high capability (causing SystemException in latest  | 2020/10/11 |
|            |   version of spidev on 5.4 kernel line)                             |            |
+------------+---------------------------------------------------------------------+------------+
| **1.17.1** | * Add cmdline opt: "pcf8574" and "bitbang_6800" interfaces          | 2020/09/26 |
+------------+---------------------------------------------------------------------+------------+
| **1.17.0** | * Added --inverse option for ST7735 to cmdline opt                  | 2020/09/25 |
|            | * Allow SPI interface to define reset duration                      |            |
|            | * Change bitmap_font to be compatible with Pillow < 7.0             |            |
+------------+---------------------------------------------------------------------+------------+
| **1.16.2** | * Added new parallel interface module                               | 2020/09/20 |
|            | * Renamed parallel class to bitbang_6800; moved to parallel module  |            |
+------------+---------------------------------------------------------------------+------------+
| **1.16.1** | * Fix bug in bitmap_font: glyph_index now computed correctly        | 2020/08/29 |
+------------+---------------------------------------------------------------------+------------+
| **1.16.0** | * Embedded font parallel device (for upcoming HD44780, Winstar      | 2020/08/27 |
|            |   character devices)                                                |            |
+------------+---------------------------------------------------------------------+------------+
| **1.15.0** | * Parallel bus and I²C backpack support                             | 2020/08/10 |
+------------+---------------------------------------------------------------------+------------+
| **1.14.1** | * Pin spidev at v3.4 or lower; v3.5 seems to cause SystemException  | 2020/07/26 |
|            |   running on latest linux kernel                                    |            |
|            | * Fix bug in snapshot: should always redraw on startup              |            |
+------------+---------------------------------------------------------------------+------------+
| **1.14.0** | * Drop support for Python 2.7, only 3.5 or newer is supported now   | 2020/04/07 |
|            | * Add support for SPI mode (clock polarity and phase)               |            |
+------------+---------------------------------------------------------------------+------------+
| **1.13.0** | * Add support for using any GPIO pin as a CS pin for SPI            | 2020/01/12 |
+------------+---------------------------------------------------------------------+------------+
| **1.12.0** | * Rework namespace support for subprojects                          | 2019/06/15 |
+------------+---------------------------------------------------------------------+------------+
| **1.11.0** | * Support luma.lcd.aux (if present)                                 | 2019/06/02 |
+------------+---------------------------------------------------------------------+------------+
| **1.10.1** | * Fix [Error 22] emitted from within I2C serial adapter when used   | 2019/05/25 |
|            |   with SSD1327 device                                               |            |
+------------+---------------------------------------------------------------------+------------+
| **1.10.0** | * Allow viewport pseudo-display to dither when rendering to         | 2019/05/23 |
|            |   device with lower-fidelity color mode                             |            |
+------------+---------------------------------------------------------------------+------------+
| **1.9.0**  | * Improve I2C render speed by not chunking into 32-byte blocks      | 2019/05/10 |
|            | * Add support for bridging FTDI to I2C/SPI                          |            |
+------------+---------------------------------------------------------------------+------------+
| **1.8.3**  | * Improve command line help output                                  | 2019/01/07 |
|            | * Split API docs into separate pages                                |            |
+------------+---------------------------------------------------------------------+------------+
| **1.8.2**  | * Fix type hint for SPI's cs_high parameter                         | 2018/11/05 |
+------------+---------------------------------------------------------------------+------------+
| **1.8.1**  | * Mutable string now works over unicode (for both py2/3)            | 2018/09/18 |
+------------+---------------------------------------------------------------------+------------+
| **1.8.0**  | * Namespace packaging fix                                           | 2018/09/04 |
|            | * Correct implementation of pkgutil style namespace                 |            |
|            | * Support for Python 3.7                                            |            |
|            | * Docstring updates                                                 |            |
+------------+---------------------------------------------------------------------+------------+
| **1.7.2**  | * Fix upside-down SEG7_FONT                                         | 2018/03/29 |
+------------+---------------------------------------------------------------------+------------+
| **1.7.1**  | * Support unicode in terminal class                                 | 2018/03/22 |
+------------+---------------------------------------------------------------------+------------+
| **1.7.0**  | * Add ``persist`` flag on device                                    | 2018/03/21 |
+------------+---------------------------------------------------------------------+------------+
| **1.6.0**  | * Add ``--spi-transfer-size=...`` flag in cmdline args              | 2018/02/21 |
+------------+---------------------------------------------------------------------+------------+
| **1.5.0**  | * Add SEG7_FONT: Compact 7x3 font for LED Matrix                    | 2018/02/06 |
+------------+---------------------------------------------------------------------+------------+
| **1.4.0**  | * Add ``--spi-cs-high=...`` flag in cmdline args                    | 2018/01/29 |
+------------+---------------------------------------------------------------------+------------+
| **1.3.0**  | * Add ``--gpio-mode=...`` flag in cmdline args                      | 2018/01/02 |
+------------+---------------------------------------------------------------------+------------+
| **1.2.1**  | * Use ``extras_require`` in ``setup.py`` for Linux dependencies     | 2017/11/26 |
+------------+---------------------------------------------------------------------+------------+
| **1.2.0**  | * Added ``get_library_version`` & ``get_library_for_display_type``  | 2017/11/23 |
+------------+---------------------------------------------------------------------+------------+
| **1.1.1**  | * Version number available as ``luma.core.__version__`` now         | 2017/11/23 |
+------------+---------------------------------------------------------------------+------------+
| **1.1.0**  | * Added image composition classes                                   | 2017/10/28 |
+------------+---------------------------------------------------------------------+------------+
| **1.0.3**  | * Explicitly state 'UTF-8' encoding in setup when reading files     | 2017/10/18 |
+------------+---------------------------------------------------------------------+------------+
| **1.0.2**  | * Fix conditional install on wheel                                  | 2017/09/15 |
+------------+---------------------------------------------------------------------+------------+
| **1.0.1**  | * Don't install RPi.GPIO & spidev if setup running on OSX           | 2017/09/04 |
+------------+---------------------------------------------------------------------+------------+
| **1.0.0**  | * Stable release (remove all deprecated methods & parameters)       | 2017/07/29 |
+------------+---------------------------------------------------------------------+------------+
| **0.9.5**  | * Remove assert in ``terminal`` to allow extended characters to be  | 2017/07/06 |
|            |   printed (note: this only works for Python3 presently)             |            |
+------------+---------------------------------------------------------------------+------------+
| **0.9.4**  | * Add ``tolerant`` class for legacy font handling non-ASCII chars   | 2017/07/01 |
|            | * Add CP437 chars to fonts.py                                       |            |
+------------+---------------------------------------------------------------------+------------+
| **0.9.3**  | * LCD_FONT: lowercase cyrillic chars added, minor corrections in    | 2017/06/25 |
|            |   uppercase chars                                                   |            |
+------------+---------------------------------------------------------------------+------------+
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
