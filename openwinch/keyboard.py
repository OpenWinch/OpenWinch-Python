#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from openwinch.input import InputType

import threading
import click


class Keyboard(object):

    __winch = None
    __controlLoop = None

    def __init__(self, winch):
        self.__winch = winch
        self.__controlLoop = threading.Thread(target=self.__runControlLoop, name="Kbd", args=(), daemon=True)
        self.__controlLoop.start()

    def __runControlLoop(self):
        input = InputType.UP
        while(input is not None):
            input = self.get()
            self.__winch.enterGui(input)

    def get(self) -> InputType:
        try:
            k = click.getchar()
            if k == '\x1b[A':
                return InputType.UP
            elif k == '\x1b[B':
                return InputType.DOWN
            elif k == '\x1b[C':
                return InputType.RIGHT
            elif k == '\x1b[D':
                return InputType.LEFT
            else:
                print("not an arrow key!\n")
        except Exception as ex:
            return None
