ChangeLog
---------

+------------+---------------------------------------------------------------------+------------+
| Version    | Description                                                         | Date       |
+============+=====================================================================+============+
| *Upcoming* | *TBC*                                                               |            |
+------------+---------------------------------------------------------------------+------------+
| **0.4.1**  | * Refactor framebuffer interface                                    | 2017/02/27 |
+------------+---------------------------------------------------------------------+------------+
| **0.4.0**  | * Add spritesheet and framerate_regulator functionality             | 2017/02/27 |
|            | * Add full-frame and diff-to-previous framebuffer implementations   |            |
|            | * Remove unnecessary travis/tox dependencies                        |            |
+------------+---------------------------------------------------------------------+------------+
| **0.3.2*** | * Bug fix: ``legacy.show_message`` wrong device height              | 2017/02/24 |
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
