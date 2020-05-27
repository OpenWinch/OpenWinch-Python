#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from openwinch.controller import Winch
from openwinch.hardware import (Board, SpeedMode)
from openwinch.hardware_config import (IN_REVERSE,
                                       OUT_REVERSE,
                                       IN_MOVE_LEFT,
                                       IN_MOVE_RIGHT,
                                       OUT_SPD,
                                       OUT_PWR,
                                       OUT_THROTTLE)
from openwinch.logger import logger

from gpiozero import Button, PWMOutputDevice, OutputDevice


class RaspberryPi(Board):

    def __init__(self, winch: Winch):
        logger.debug("IO : Initialize Hardware...")
        super().__init__(winch)

        # Power
        self.__power_cmd = OutputDevice(OUT_PWR)
        self.__power_cmd.off()

        # Reverse
        self.__reverse_btn = Button(IN_REVERSE)
        self.__reverse_cmd = OutputDevice(OUT_REVERSE)

        # Move
        self.__move_left_btn = Button(IN_MOVE_LEFT)
        self.__move_right_btn = Button(IN_MOVE_RIGHT)

        # Speed mode (Lo, Medium, Hi)
        self.__speed_cmd = OutputDevice(OUT_SPD)

        # Throlle
        self.__throttle_cmd = PWMOutputDevice(OUT_THROTTLE)

        # Register event
        self.__reverse_btn.when_pressed = self.__pressedReverse
        self.__reverse_btn.when_held = self.__pressedInit
        self.__move_left_btn = self.__pressedLeft
        self.__move_right_btn = self.__pressedRight

    def __pressedRight(self):
        logger.debug("IO : Move Right pressed !")

    def __pressedLeft(self):
        logger.debug("IO : Move Left pressed !")

    def __pressedInit(self):
        logger.debug("IO : Init/Reset pressed !")
        self.setSpeedMode(SpeedMode.HIGH)  # TODO(Mick) : validate with motor

    def __pressedReverse(self):
        logger.debug("IO : Reverse pressed !")
        self.setReverse(not self.isReverse())

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
