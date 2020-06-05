#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from luma.core.render import canvas
from luma.core.sprite_system import framerate_regulator
from PIL import ImageFont

from abc import ABC, abstractmethod
from enum import Enum, unique

import sys
import threading

from openwinch.config import config
from openwinch.constantes import SPEED_UNIT, WINCH_DISTANCE
from openwinch.input import InputType
from openwinch.logger import logger
from openwinch.display_config import (ITEM_BACK,
                                      COLOR_PRIM_FONT,
                                      COLOR_PRIM_BACK,
                                      COLOR_SELC_FONT,
                                      COLOR_SELC_BACK,
                                      FONT_TEXT,
                                      FONT_ICON,
                                      FONT_LOGO)
from openwinch.hardware_config import (LCD_HEIGHT, LCD_WIDTH, LCD_ADDR, LCD_FPS)
from openwinch.version import __version__


@unique
class GuiType(Enum):
    DISABLE = 0
    SH1106_I2C = 1
    VGA = 100
    CAPTURE = 101


class Gui(object):

    cursor_pos = 1
    view_pos = 0

    __winch = None
    __device = None
    screen = None

    # distance = 1

    def __init__(self, winch):
        if (config.GUI == GuiType.SH1106_I2C.name):
            from luma.core.interface.serial import i2c
            from luma.oled.device import sh1106

            serial_interface = i2c(port=1, address=LCD_ADDR)
            self.__device = sh1106(serial_interface, width=LCD_WIDTH, height=LCD_HEIGHT, rotate=0)
        elif (config.GUI == GuiType.VGA.name):
            from luma.emulator.device import pygame

            self.__device = pygame(width=LCD_WIDTH, height=LCD_HEIGHT, rotate=0, mode='1', transform='scale2x', scale=2, frame_rate=60)
        elif (config.GUI == GuiType.CAPTURE.name):
            from luma.emulator.device import capture

            self.__device = capture(width=LCD_WIDTH, height=LCD_HEIGHT, rotate=0, mode='1', transform='scale2x', scale=2, file_template="docs/images/screens/OpenWinch_{0:06}.png")

        self.__winch = winch
        self.__device.show()
        self.__font = ImageFont.truetype(FONT_TEXT, 8)
        self.__regulator = framerate_regulator(fps=LCD_FPS)

        self.screen = MainScreen(self)

    def getWinch(self):
        return self.__winch

    def __drawBoot(self):
        with canvas(self.__device) as draw:
            font_size = 20
            name = "OpenWinch"

            x = (LCD_WIDTH / 2) - (len(name) / 2 * font_size / 2)
            xver = (LCD_WIDTH / 2) + (((len(name) / 2) - 1) * font_size / 2)
            y = (LCD_HEIGHT / 2) - (font_size / 2)
            yver = y + font_size

            draw.text((x, y), name, fill=COLOR_PRIM_FONT, font=ImageFont.truetype(FONT_LOGO, font_size))
            draw.text((xver, yver), __version__, fill=COLOR_PRIM_FONT, font=ImageFont.truetype(FONT_TEXT, 8))

    def boot(self):
        self.__drawBoot()
        self.__display_draw_Loop = threading.Thread(target=self.__draw_loop, name="display", args=(), daemon=True)
        self.__display_draw_Loop.start()

    def display(self):
        with canvas(self.__device) as draw:
            self.screen.display(draw)

    def getPos(self):
        return self.cursor_pos

    def enter(self, key):
        # Directional Common
        if (InputType.RIGHT == key):
            self.cursor_pos += 1
        elif (InputType.LEFT == key):
            self.cursor_pos -= 1
        elif (InputType.ENTER == key):
            self.screen.enter(self.cursor_pos)

        # out bound fix
        if (self.cursor_pos < 0):
            if (self.screen.countItems() - 1 > 0):
                self.cursor_pos = self.screen.countItems() - 1
            else:
                self.cursor_pos = 0
        elif (self.cursor_pos > self.screen.countItems() - 1):
            self.cursor_pos = 0

    def statusBar(self, draw):
        # Battery
        battery_value = self.__winch.getBattery()

        battery_symbol = ""
        if (battery_value > 87.5):
            battery_symbol = ""
        elif (battery_value > 62.5):
            battery_symbol = ""
        elif (battery_value > 37.5):
            battery_symbol = ""
        elif (battery_value > 12.5):
            battery_symbol = ""

        battery_x = 2
        draw.text((battery_x, 0), battery_symbol, fill=COLOR_PRIM_FONT, font=ImageFont.truetype(FONT_ICON, 8))
        draw.text((battery_x + 15, 1), "%s%%" % battery_value, fill=COLOR_PRIM_FONT, font=self.__font)

        # Wifi
        wifi_x = 105
        draw.text((wifi_x, 0), "", fill=COLOR_PRIM_FONT, font=ImageFont.truetype(FONT_ICON, 8))
        draw.text((wifi_x + 7, 1), "%s " % self.__winch.getRemote(), fill=COLOR_PRIM_FONT, font=self.__font)

    def createValue(self, draw, title, value):
        draw.text((0, 0), title, fill=COLOR_PRIM_FONT, font=ImageFont.truetype(FONT_TEXT, 12))
        draw.rectangle([0, 12, LCD_WIDTH, 12], fill="white", outline="white")
        draw.text((2, 18), "%s" % value, fill=COLOR_PRIM_FONT, font=ImageFont.truetype(FONT_TEXT, 14))

        y = 0.78 * LCD_HEIGHT
        draw.rectangle([0, y, LCD_WIDTH, LCD_HEIGHT], fill="white", outline="white")
        draw.text((0, 0.80 * LCD_HEIGHT), "exit to save...", fill="black", font=ImageFont.truetype(FONT_TEXT, 12))

    def createMenuScroll(self, draw, items, selected_item=None):
        font_size = 12
        draw_cursor_pos = 0
        draw_view_pos = 0

        cursor_limit_screen = (LCD_HEIGHT / font_size) - 1
        if (self.cursor_pos > cursor_limit_screen):
            draw_view_pos = -((self.cursor_pos - cursor_limit_screen) * font_size)

        for item in items:
            text_color = COLOR_PRIM_FONT
            y = draw_cursor_pos * font_size

            if (self.cursor_pos == draw_cursor_pos):
                text_color = "black"
                draw.rectangle([0, draw_view_pos + y, LCD_WIDTH, draw_view_pos + y + font_size], fill="white", outline="white")

            if (selected_item is not None and selected_item == item):
                draw.text((LCD_WIDTH - font_size, draw_view_pos + y), "", fill=text_color, font=ImageFont.truetype(FONT_ICON, font_size - 2))
            draw.text((1, draw_view_pos + y), item, fill=text_color, font=ImageFont.truetype(FONT_TEXT, font_size))
            draw_cursor_pos += 1

    def createMenuIcon(self, draw, items):
        font_size = 12
        btn_width = LCD_WIDTH / 3
        btn_start = ((btn_width - font_size) / 2) + 1
        btn_height = 0.78 * LCD_HEIGHT
        draw_cursor_pos = 0

        for item in items:
            bgd = "white"
            fnt = "black"

            if (draw_cursor_pos == self.cursor_pos):
                bgd = "black"
                fnt = "white"

            draw.rectangle([draw_cursor_pos * btn_width, btn_height, (draw_cursor_pos + 1) * btn_width, LCD_HEIGHT], fill=bgd, outline=fnt)
            draw.text((btn_start + draw_cursor_pos * btn_width, 0.79 * LCD_HEIGHT), items[draw_cursor_pos], fill=fnt, font=ImageFont.truetype(FONT_ICON, font_size))
            draw_cursor_pos += 1

    def __draw_loop(self):
        t = threading.currentThread()
        if (config.GUI != GuiType.DISABLE.name and config.GUI != GuiType.CAPTURE.name):
            while getattr(t, "do_run", True):
                with self.__regulator:
                    if (self.__winch.getState().isBoot):
                        self.display()
                    else:
                        self.__drawBoot()
        else:
            self.extractScreen

    def extractScreen(self):
        # Capture mode for DOC
        self.display()

        # Stop Screen 003
        self.enter(InputType.ENTER)
        self.display()

        # Play Screen
        self.enter(InputType.ENTER)

        # Menu Screen 004 & 005
        self.enter(InputType.RIGHT)
        self.display()
        self.enter(InputType.ENTER)
        self.display()

        # Manual postition 006 & 007
        self.enter(InputType.RIGHT)
        self.display()
        self.enter(InputType.ENTER)
        self.display()
        self.enter(InputType.ENTER)

        # Security distance 008 & 009
        self.enter(InputType.RIGHT)
        self.enter(InputType.RIGHT)
        self.display()
        self.enter(InputType.ENTER)
        self.display()
        self.enter(InputType.ENTER)

        # Mode Selector 010 & 011
        self.enter(InputType.RIGHT)
        self.enter(InputType.RIGHT)
        self.enter(InputType.RIGHT)
        self.display()
        self.enter(InputType.ENTER)
        self.display()
        self.enter(InputType.RIGHT)
        self.display()
        self.enter(InputType.ENTER)

        # Mode Velocity Start 012 & 013
        self.enter(InputType.RIGHT)
        self.enter(InputType.RIGHT)
        self.enter(InputType.RIGHT)
        self.enter(InputType.RIGHT)
        self.display()
        self.enter(InputType.ENTER)
        self.display()
        self.enter(InputType.ENTER)

        # Mode Velocity Stop 014 & 015
        self.enter(InputType.RIGHT)
        self.enter(InputType.RIGHT)
        self.enter(InputType.RIGHT)
        self.enter(InputType.RIGHT)
        self.enter(InputType.RIGHT)
        self.display()
        self.enter(InputType.ENTER)
        self.display()
        self.enter(InputType.ENTER)


class ScreenBase(ABC):

    _gui = None
    _winch = None

    def __init__(self, gui):
        self._gui = gui
        self._gui.cursor_pos = 0
        self._gui.view_pos = 0
        self._winch = self._gui.getWinch()

    @abstractmethod
    def countItems(self) -> int:
        pass

    @abstractmethod
    def display(self, draw):
        pass

    @abstractmethod
    def enter(self, cursor_pos):
        pass


class MainScreen(ScreenBase):
    __ITEMS_IDLE = ["", "", ""]
    __ITEMS_RUNNING = ["", "", ""]
    __ITEMS_ERROR = ["", "", ""]
    __count = 1

    def countItems(self) -> int:
        return len(self.__ITEMS_IDLE)

    def display(self, draw):
        self.__count += 2
        self.__inver = True

        # Status bar
        self._gui.statusBar(draw)

        # Speed
        speed_x = 54
        draw.text((speed_x, 14), "%s" % self._winch.getSpeedTarget(), fill="white", font=ImageFont.truetype(FONT_TEXT, 35))
        draw.text((speed_x + 40, 28), SPEED_UNIT, fill="white", font=ImageFont.truetype(FONT_TEXT, 15))  # Very good

        # Distance
        marg = 4
        percent = 1 / WINCH_DISTANCE * self._winch.getDistance()
        draw.rectangle([0 + marg, 11, ((LCD_WIDTH - marg) * percent), 14], fill="white", outline="white")

        if (self._winch.getState().isStop):
            self._gui.createMenuIcon(draw, self.__ITEMS_IDLE)
        elif (self._winch.getState().isRun):
            self._gui.createMenuIcon(draw, self.__ITEMS_RUNNING)
            self.__animateDistance(draw)
        else:
            self._gui.createMenuIcon(draw, self.__ITEMS_ERROR)

    def __animateDistance(self, draw):
        cursor_size = 2
        stepper = 10
        if (self.__count >= stepper):
            self.__count = 1

        if(self.__count % stepper != 0):
            for i in range(0, int(LCD_WIDTH / stepper), 1):
                draw.rectangle([self.__count + (i * stepper), 11, (self.__count + (i * stepper)) + cursor_size, 14], fill="black", outline="black")

    def enter(self, cursor_pos):
        if (0 == cursor_pos):
            if (self._winch.getState().isStop):
                self._winch.start()
            else:
                self._winch.stop()
        if (1 == cursor_pos):
            self._gui.screen = MenuScreen(self._gui)
        if (2 == cursor_pos):
            pass


class MenuScreen(ScreenBase):
    __ITEMS_MENU = [
        ITEM_BACK,
        "Manual position",
        "Security distance",
        "Mode selector",
        "Velocity Start",
        "Velocity Stop",
    ]
    # __ITEMS = ["", "", ""]

    def countItems(self) -> int:
        return len(self.__ITEMS_MENU)

    def display(self, draw):
        self._gui.createMenuScroll(draw, self.__ITEMS_MENU)

    def enter(self, cursor_pos):
        if (0 == cursor_pos):
            self._gui.screen = MainScreen(self._gui)
        else:
            if (1 == cursor_pos):
                self._gui.screen = ManualPositionScreen(self._gui)
            elif (2 == cursor_pos):
                self._gui.screen = SecurityDistanceScreen(self._gui)
            elif (3 == cursor_pos):
                self._gui.screen = ModeSelectorScreen(self._gui)
            elif (4 == cursor_pos):
                self._gui.screen = VelocityStartScreen(self._gui)
            elif (5 == cursor_pos):
                self._gui.screen = VelocityStopScreen(self._gui)


class ManualPositionScreen(ScreenBase):

    def __init__(self, gui):
        super(ManualPositionScreen, self).__init__(gui)
        # Load from item
        self._gui.cursor_pos = sys.maxsize / 2

    def countItems(self) -> int:
        return sys.maxsize

    def display(self, draw):
        draw.text((1, 1), "Move with Right/Left button.", fill=COLOR_PRIM_FONT, font=ImageFont.truetype(FONT_TEXT, 12))

        y = 0.78 * LCD_HEIGHT
        draw.rectangle([0, y, LCD_WIDTH, LCD_HEIGHT], fill="white", outline="white")
        draw.text((0, 0.80 * LCD_HEIGHT), "enter to exit.", fill="black", font=ImageFont.truetype(FONT_TEXT, 12))

    def enter(self, cursor_pos):
        self._gui.screen = MenuScreen(self._gui)


class SecurityDistanceScreen(ScreenBase):
    TITLE = "Security distance"
    value = 10

    def __init__(self, gui):
        super(SecurityDistanceScreen, self).__init__(gui)
        # Load from item
        self._gui.cursor_pos = self.value

    def countItems(self) -> int:
        return 255

    def display(self, draw):
        self._gui.createValue(draw, self.TITLE, self._gui.getPos())

    def enter(self, cursor_pos):
        #  Save to item
        self._gui.screen = MenuScreen(self._gui)


class ModeSelectorScreen(ScreenBase):
    __TITLE = "Mode selector"
    __ITEMS = [
        ITEM_BACK,
        "OneWay",
        "TwoWay",
    ]

    def __init__(self, gui):
        super(ModeSelectorScreen, self).__init__(gui)
        # Load from item
        # self._gui.cursor_pos = 0

    def countItems(self) -> int:
        return len(self.__ITEMS)

    def display(self, draw):
        self._gui.createMenuScroll(draw, self.__ITEMS, "OneWay")

    def enter(self, cursor_pos):
        #  Save to item
        self._gui.screen = MenuScreen(self._gui)


class VelocityStartScreen(ScreenBase):
    TITLE = "Velocity Start"
    value = 10

    def __init__(self, gui):
        super(VelocityStartScreen, self).__init__(gui)
        # Load from item
        self._gui.cursor_pos = self.value

    def countItems(self) -> int:
        return 255

    def display(self, draw):
        self._gui.createValue(draw, self.TITLE, self._gui.getPos())

    def enter(self, cursor_pos):
        #  Save to item
        self._gui.screen = MenuScreen(self._gui)


class VelocityStopScreen(ScreenBase):
    TITLE = "Velocity Stop"
    value = 10

    def __init__(self, gui):
        super(VelocityStopScreen, self).__init__(gui)
        # Load from item
        self._gui.cursor_pos = self.value

    def countItems(self) -> int:
        return 255

    def display(self, draw):
        self._gui.createValue(draw, self.TITLE, self._gui.getPos())

    def enter(self, cursor_pos):
        #  Save to item
        self._gui.screen = MenuScreen(self._gui)
