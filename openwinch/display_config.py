#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

UP=1
RIGHT=2
DOWN=3
LEFT=4
ENTER=DOWN

ITEM_BACK = "< BACK"

COLOR_PRIM_FONT = "white"
COLOR_PRIM_BACK = "black"
COLOR_SELC_FONT = "black"
COLOR_SELC_BACK = "white"

# 0=Disable, 1=Oled , 2=Emulator , 3=Capture
mode=2

font_path = "openwinch/fonts/FreePixel.ttf"
font_path2 = "openwinch/fonts/fontawesome-webfont.ttf"
font_path3 = "openwinch/fonts/SLANT.TTF"