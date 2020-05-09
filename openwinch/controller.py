#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from openwinch.version import __version__
from enum import Enum

import atexit
import logging
import threading
import time

# Constants
SPEED_MAX = 35
SPEED_MIN = 1
LOOP_DELAY = 0.01
#LOOP_DELAY = 0.1

class State(Enum):
    """ State of Winch. """
    ERROR   = -999
    UNKNOWN = -1
    INIT    = 0
    IDLE    = 1
    START   = 2
    RUNNING = 3
    STOP    = 4

class Winch(object):
    """ Winch controller class. """

    __state = State.UNKNOWN
    __speed_current  = 0
    __speed_target   = 28
    __velocity_start = 1
    __velocity_stop  = 3
    #__controlLoop
    #__log

    def __init__(self):
        """ Constructor of Winch class. """

        # Always pass in emergency mode when Application halt/exit !!!
        atexit.register(self.emergency)
        threading.currentThread().setName("Main")

        self.__initLogger()
        self.__initControlLoop()

    def __del__(self):
        """ Destructor of Winch class. """

        self.__controlLoop.do_run = False
        self.__controlLoop.join()

    def __banner(self):
        self.__log.info("""
   ____                 _       ___            __  
  / __ \____  ___  ____| |     / (_)___  _____/ /_ 
 / / / / __ \/ _ \/ __ \ | /| / / / __ \/ ___/ __ \\
/ /_/ / /_/ /  __/ / / / |/ |/ / / / / / /__/ / / /
\____/ .___/\___/_/ /_/|__/|__/_/_/ /_/\___/_/ /_/ 
    /_/                                            Ver. %s""" % __version__)

    def __initLogger(self):
        """ Initialize logger. """

        self.__log = logging.getLogger('OpenWinch')
        self.__log.setLevel(logging.DEBUG)
        self.__log.debug("Initialize Logger...")

        # Create file handler which logs even debug messages
        fh = logging.FileHandler('openwinch.log')
        fh.setLevel(logging.DEBUG)

        # Create console handler with a info log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s.%(threadName)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Add the handlers to the logger
        self.__log.addHandler(fh)
        self.__log.addHandler(ch)

        self.__banner()
        self.__log.debug("Started Logger.")

    def __initControlLoop(self):
        """ Initialize Control Loop thread. """

        self.__log.debug("Initialize Control Loop...")
        self.__controlLoop = threading.Thread(target=self.__runControlLoop, name="Ctrl", args=(), daemon=True)
        self.__controlLoop.start()

    def initialize(self):
        """ Initialise Hardware.

        Step :
        - Initialise Sensor
        - Position at origin
        """

        self.__log.debug("Initialize Winch hardware...")
        self.__changeMode(State.INIT)
        # Split in two function
        self.__changeMode(State.IDLE)
        self.__log.info("Initialized Winch !")

    def __runControlLoop(self):
        """ Main Loop to control hardware. """

        t = threading.currentThread()
        self.__log.debug("Starting Control Loop.")

        while getattr(t, "do_run", True):
            self.__log.debug("Current state : %s - speed : %s" % (self.__state, self.__speed_current))
            
            if (self.__state == State.RUNNING or self.__state == State.START):
                if (self.__speed_current < self.__speed_target):
                    self.__speed_current += self.__velocity_start
                    if (self.__speed_current >= self.__speed_target):
                        self.__started()

                if (self.__speed_current > self.__speed_target):
                    self.__speed_current -= self.__velocity_stop
                
            elif (self.__state == State.STOP):
                if (self.__speed_current > 0):
                    self.__speed_current -= self.__velocity_stop
                elif (self.__speed_current <= 0):
                    self.__speed_current = 0
                    self.__stoped()

            elif (self.__state == State.ERROR):
                self.__speed_current = 0
            
            time.sleep(LOOP_DELAY)
        self.__log.debug("Stopping Control Loop.")

    def start(self):
        """ Command Start winch. """

        self.__log.info("Press Start")

        if (self.__state == State.IDLE or self.__state == State.STOP):
            self.__changeMode(State.START)

        elif (self.__state == State.START):
            self.__log.warning("Switch mode alway enable !")

        else:
            self.__log.error("Not possible to start, re-initialize Winch !")

    def __started(self):
        """ Call when hardware process start completely. """

        if (self.__state == State.START):
            self.__changeMode(State.RUNNING)

    def stop(self):
        """ Command Stop winch """

        self.__log.info("Press Stop")

        if (self.__state == State.RUNNING or self.__state == State.START):
            self.__changeMode(State.STOP)

        elif (self.__state == State.STOP):
            self.__log.warning("Switch mode alway enable !")

        else:
            self.__log.error("Not possible to stop, re-initialize Winch !")
    
    def __stoped(self):
        """ Call when hardware stop completely. """

        if (self.__state == State.STOP):
            self.__changeMode(State.IDLE)
    
    def emergency(self):
        """ Command Emergency winch. """

        self.__log.fatal("HALT EMERGENCY")
        self.__changeMode(State.ERROR)

    def display(self):
        """ Process display in console. """

        print("State\t: %s\nTarget Speed\t: %s\nCurrent speed\t: %s" % (self.__state, self.__speed_target, self.__speed_current))

    def __changeMode(self, mode):
        """ Change State mode of machine-state
        
        Parameters
        ----------
        mode : State Enum
            Mode to enable.
        """

        self.__log.debug("Switch mode : %s", mode)
        self.__state = mode

    def getSpeedTarget(self):
        return self.__speed_target

    def getState(self):
        return self.__state

    def speedUp(self, value=1):
        """ Up speed.

        Parameters
        ----------
        value : int, optional
            Value to increment speed (default is 1)
        """
        if (self.__speed_target < SPEED_MAX):
            self.__speed_target += value

    def speedDown(self, value=1):
        """ Down speed.

        Parameters
        ----------
        value : int, optional
            Value to decrement speed (default is 1)
        """
        if (self.__speed_target > SPEED_MIN):
            self.__speed_target -= value

    def speedValue(self, value):
        """ Set speed. """
        if (value >= SPEED_MIN or value < SPEED_MAX):
            self.__speed_target = value

winch = Winch()