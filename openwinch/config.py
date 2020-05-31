#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from os import environ


class Config(object):
    BOARD = environ.get('OW_BOARD', 'openwinch.hardwarePi.RaspberryPi')
    MODE = environ.get('OW_MODE', 'ModeType.OneWay')


config = Config()
