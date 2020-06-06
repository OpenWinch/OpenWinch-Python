#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from openwinch.controller import Winch
from openwinch.hardware import (Board, SpeedMode)
from openwinch.hardware_config import (IN_KEY_ENTER,
                                       IN_KEY_LEFT,
                                       IN_KEY_RIGHT,
                                       OUT_REVERSE,
                                       OUT_SPD,
                                       OUT_PWR,
                                       OUT_THROTTLE)
from openwinch.input import InputType
from openwinch.logger import logger

from gpiozero import Button, PWMOutputDevice, OutputDevice


class RaspberryPi(Board):

    __power_cmd = None
    __reverse_cmd = None
    __speed_cmd = None
    __throttle_cmd = None
    __key_enter_btn = None
    __key_left_btn = None
    __key_right_btn = None

    def __init__(self, winch: Winch):
        logger.debug("IO : Initialize Hardware...")
        super().__init__(winch)

        # Power
        self.__power_cmd = OutputDevice(OUT_PWR)
        self.__power_cmd.off()

        # Reverse
        self.__reverse_cmd = OutputDevice(OUT_REVERSE)

        # Speed mode (Lo, Medium, Hi)
        self.__speed_cmd = OutputDevice(OUT_SPD)

        # Throlle
        self.__throttle_cmd = PWMOutputDevice(OUT_THROTTLE)

        # Move
        self.__key_enter_btn = Button(IN_KEY_ENTER)
        self.__key_left_btn = Button(IN_KEY_LEFT)
        self.__key_right_btn = Button(IN_KEY_RIGHT)

        # Register event
        self.__key_enter_btn.when_pressed = self.__pressedEnter
        self.__key_left_btn = self.__pressedLeft
        self.__key_right_btn = self.__pressedRight

    def __pressedRight(self):
        logger.debug("IO : Move Right pressed !")
        self._winch.enterGui(InputType.RIGHT)

    def __pressedLeft(self):
        logger.debug("IO : Move Left pressed !")
        self._winch.enterGui(InputType.LEFT)

    def __pressedEnter(self):
        logger.debug("IO : Enter pressed !")
        self._winch.enterGui(InputType.ENTER)

    def initialize(self):
        """ Initialize """
        super().initialize()
        self.setReverse(False)
        self.setSpeedMode(SpeedMode.LOW)
        self.__throttle_cmd.value = 0
        self.__throttle_cmd.on()

        self.__power_cmd.on()
        logger.info("IO : Hardware Initialized !")

    def emergency(self):
        logger.debug("IO : Shutdown power !")
        self.__power_cmd.off()

    def setThrottleValue(self, value):
        if (self.__throttle_cmd.value != value):
            logger.debug("IO : Throttle to %s" % value)
            self.__throttle_cmd.value = value

    def getThrottleValue(self):
        return self.__throttle_cmd.value

    def setSpeedMode(self, speed_mode):
        super().setSpeedMode(speed_mode)
        if (self._speed_mode == SpeedMode.LOW):
            self.__speed_cmd.off()
        # elif (self._speed_mode == SpeedMode.MEDIUM):
        #     self.__speed_cmd.off()
        elif (self._speed_mode == SpeedMode.HIGH):
            self.__speed_cmd.on()

    def setReverse(self, enable):
        super().setReverse(enable)
        if (self._reverse):
            self.__reverse_cmd.off()
        else:
            self.__reverse_cmd.on()
