# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

import time
import math

from gpiozero import Button

from hardware_config import IN_HS_W, IN_HS_V, IN_HS_U
from constantes import MOTOR_PPR, WINCH_DIAM

CW = 1      # Assign a value to represent clock wise rotation
CCW = -1    # Assign a value to represent counter-clock wise rotation

millis = lambda: int(round(time.time() * 1000))


class Tachometer(object):

    __direct = CW

    # Sensor
    _hsu = Button(IN_HS_U)
    _hsw = Button(IN_HS_W)
    _hsv = Button(IN_HS_V)

    pulseTimeU = 0
    pulseTimeW = 0
    pulseTimeV = 0

    pulseCountU = 0
    pulseCountW = 0
    pulseCountV = 0

    __startTimeU = millis()
    __startTimeW = millis()
    __startTimeV = millis()

    __prevTimeU = 0
    __prevTimeW = 0
    __prevTimeV = 0

    rpmU = 0
    rpmW = 0
    rpmV = 0

    def __init__(self):
        self._hsu.when_pressed = self.hallSensorU
        self._hsw.when_pressed = self.hallSensorW
        self._hsv.when_pressed = self.hallSensorV

    def __get_rpm(self, pulseTime):
        # Calculate the pulses per min (1000 millis in 1 second)
        # (1000 / pulseTime) * 60
        PPM = (60000 / pulseTime)
        # Calculate revs per minute based on number of pulses per rev
        RPM = PPM / (MOTOR_PPR / 3)

        return RPM

    def hallSensorW(self):
        print("Pulse W")
        # Set startTime to current microcontroller elapsed time value
        self.__startTimeW = millis()

        # Read the current W hall sensor value
        ___HSW_Val = self._hsw.is_pressed
        # Read the current V (or U) hall sensor value
        ___HSV_Val = self._hsv.is_pressed
        # Determine rotation __direction (ternary if statement)
        self.__direct = CW if ___HSW_Val == ___HSV_Val else CCW

        # Calculate the current time between pulses W
        self.pulseTimeW = self.__startTimeW - self.__prevTimeW
        # Remember the start time for the next interrupt
        self.__prevTimeW = self.__startTimeW

        # Calculate Rotation Per Minute
        self.rpmW = self.__get_rpm(self.pulseTimeW)
        self.pulseCountW = self.pulseCountW + (1 * self.__direct)

    def hallSensorV(self):
        print("Pulse V")
        self.__startTimeV = millis()

        ___HSV_Val = self._hsv.is_pressed
        ___HSU_Val = self._hsu.is_pressed
        self.__direct = CW if ___HSV_Val == ___HSU_Val else CCW

        self.pulseTimeV = self.__startTimeV - self.__prevTimeV
        self.__prevTimeV = self.__startTimeV

        self.rpmV = self.__get_rpm(self.pulseTimeV)
        self.pulseCountV = self.pulseCountV + (1 * self.__direct)

    def hallSensorU(self):
        print("Pulse U")
        self.__startTimeU = millis()

        ___HSU_Val = self._hsu.is_pressed
        ___HSW_Val = self._hsw.is_pressed
        self.__direct = CW if ___HSU_Val == ___HSW_Val else CCW

        self.pulseTimeU = self.__startTimeU - self.__prevTimeU
        self.__prevTimeU = self.__startTimeU

        self.rpmU = self.__get_rpm(self.pulseTimeU)
        self.pulseCountU = self.pulseCountU + (1 * self.__direct)

    def get_rotation(self):
        return self.__direct

    def get_rpm(self):
        return (self.rpmU + self.rpmW + self.rpmV) / 3

    def get_kph(self):
        return WINCH_DIAM * self.get_rpm() * 0.1885

    def get_distance(self):
        return (math.pi * WINCH_DIAM) * self.pulseCountU
