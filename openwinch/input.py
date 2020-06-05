#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from enum import Enum


class InputType(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
    ENTER = DOWN
