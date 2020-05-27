#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# OpneWinchPy : a library for controlling the Raspberry Pi's Winch
# Copyright (c) 2020 Mickael Gaillard <mick.gaillard@gmail.com>

from luma.core.render import canvas
from luma.oled.device import sh1106
from luma.emulator.device import pygame, capture
from PIL import ImageFont

from abc import ABC, abstractmethod
import time
import sys
import click
import threading

from openwinch.hardware_config import (LCD_HEIGHT, LCD_WIDTH, LCD_ADDR)
from openwinch.display_config import (UP,
                                      LEFT,
                                      RIGHT,
                                      ENTER,
                                      DOWN,
                                      ITEM_BACK,
                                      COLOR_PRIM_FONT,
                                      COLOR_PRIM_BACK,
                                      COLOR_SELC_FONT,
                                      COLOR_SELC_BACK,
                                      LCD_MODE,
                                      font_path,
                                      font_path2,
                                      font_path3)


class Lcd(object):
    cursor_pos = 1
    view_pos = 0

    __device = None
    screen = None

    speed_value = 38
    speed_unit = "Km/h"
    distance = 1
    battery_value = 70
    wifi_value = 15
    # state 0=IDLE, 1=RUNNING, 2=EMERGENCY
    state=0

    def getPos(self):
        return self.cursor_pos

    def __init__(self):
        if (LCD_MODE == 1):
            from luma.core.interface.serial import i2c
            serial_interface = i2c(port=1, address=LCD_ADDR)
            self.__device = sh1106(serial_interface, width=LCD_WIDTH, height=LCD_HEIGHT, rotate=0)
        elif (LCD_MODE == 2):
            self.__device = pygame(width=LCD_WIDTH, height=LCD_HEIGHT, rotate=0, mode='1', transform='scale2x', scale=2, frame_rate=60)
        elif (LCD_MODE == 3):
            self.__device = capture(width=LCD_WIDTH, height=LCD_HEIGHT, rotate=0, mode='1', transform='scale2x', scale=2, file_template="docs/images/screens/OpenWinch_{0:06}.png")

        self.__device.show()
        self.__font = ImageFont.truetype(font_path, 8)

        self.screen = MainScreen(self)

    def boot(self):
        with canvas(self.__device) as draw:
            font_size = 20
            name = "OpenWinch"
            version = "1.0.0"
            x = (LCD_WIDTH / 2) - (len(name)/2 * font_size / 2)
            xver = (LCD_WIDTH / 2) + (((len(name)/2)-1) * font_size / 2)
            y = (LCD_HEIGHT / 2) - (font_size/2)
            yver = y+font_size
            draw.text((x, y), name, fill=COLOR_PRIM_FONT, font=ImageFont.truetype(font_path3, font_size))
            draw.text((xver, yver), version, fill=COLOR_PRIM_FONT, font=ImageFont.truetype(font_path, 8))

    def display(self):
        with canvas(self.__device) as draw:
            self.screen.display(draw)
        #time.sleep(2)

    def enter(self, key):
        # Directional Common
        if (RIGHT == key):
            self.cursor_pos += 1
        elif (LEFT == key):
            self.cursor_pos -= 1
        elif (DOWN == key):
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
        battery_symbol = ""
        if (self.battery_value > 87.5):
            battery_symbol = ""
        elif (self.battery_value > 62.5):
            battery_symbol = ""
        elif (self.battery_value > 37.5):
            battery_symbol = ""
        elif (self.battery_value > 12.5):
            battery_symbol = ""

        battery_x = 2
        draw.text((battery_x, 0), battery_symbol, fill=COLOR_PRIM_FONT, font=ImageFont.truetype(font_path2, 8))
        draw.text((battery_x + 15, 1), "%s%%" % self.battery_value, fill=COLOR_PRIM_FONT, font=self.__font)

        # Wifi
        wifi_x = 105
        draw.text((wifi_x, 0), "", fill=COLOR_PRIM_FONT, font=ImageFont.truetype(font_path2, 8))
        draw.text((wifi_x + 7, 1), "%s " % self.wifi_value, fill=COLOR_PRIM_FONT, font=self.__font)

    def createValue(self, draw, title, value):
        draw.text((0, 0), title, fill=COLOR_PRIM_FONT, font=ImageFont.truetype(font_path, 12))
        draw.rectangle([0, 12, LCD_WIDTH, 12], fill="white", outline="white")
        draw.text((2, 18), "%s" % value, fill=COLOR_PRIM_FONT, font=ImageFont.truetype(font_path, 14))

        y = 0.78 * LCD_HEIGHT
        draw.rectangle([0, y, LCD_WIDTH, LCD_HEIGHT], fill="white", outline="white")
        draw.text((0, 0.80 * LCD_HEIGHT), "exit to save...", fill="black", font=ImageFont.truetype(font_path, 12))

    def createMenuScroll(self, draw, items, selected_item = None):
        font_size = 12
        draw_cursor_pos = 0
        draw_view_pos = 0

        cursor_limit_screen = (LCD_HEIGHT / font_size)-1
        if (self.cursor_pos > cursor_limit_screen):
            draw_view_pos = -((self.cursor_pos - cursor_limit_screen) * font_size)

        for item in items:
            text_color = COLOR_PRIM_FONT
            y = draw_cursor_pos * font_size

            if (self.cursor_pos == draw_cursor_pos):
                text_color = "black"
                draw.rectangle([0, draw_view_pos + y, LCD_WIDTH, draw_view_pos + y +font_size], fill="white", outline="white")

            if (selected_item != None and  selected_item == item):
                draw.text((LCD_WIDTH - font_size , draw_view_pos + y), "", fill=text_color, font=ImageFont.truetype(font_path2, font_size - 2))
            draw.text((1 , draw_view_pos + y), item, fill=text_color, font=ImageFont.truetype(font_path, font_size))
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
            draw.text((btn_start + draw_cursor_pos * btn_width, 0.79 * LCD_HEIGHT), items[draw_cursor_pos], fill=fnt, font=ImageFont.truetype(font_path2, font_size))
            draw_cursor_pos += 1


class ScreenBase(ABC):

    def __init__(self, display):
        self._display = display
        self._display.cursor_pos = 0
        self._display.view_pos = 0

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
    __ITEMS_START = ["", "", ""]
    __ITEMS_STOP = ["", "", ""]

    def countItems(self) -> int:
        return len(self.__ITEMS_START)

    def display(self, draw):
        self._display.statusBar(draw)

        # Speed
        speed_x = 54
        draw.text((speed_x, 14), "%s" % self._display.speed_value, fill="white", font=ImageFont.truetype(font_path, 35))
        draw.text((speed_x + 40, 28), self._display.speed_unit, fill="white", font=ImageFont.truetype(font_path, 15))  # Very good

        # Distance
        marg = 2
        draw.rectangle([0 + marg, 11, LCD_WIDTH - marg, 14], fill="white", outline="white")

        if (self._display.state != 1):
            self._display.createMenuIcon(draw, self.__ITEMS_START)
        else:
            self._display.createMenuIcon(draw, self.__ITEMS_STOP)

    def enter(self, cursor_pos):
        if (0 == cursor_pos):
            if (self._display.state == 0):
                self._display.state = 1
            else:
                self._display.state = 0
        if (1 == cursor_pos):
            self._display.screen = MenuScreen(self._display)
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
        self._display.createMenuScroll(draw, self.__ITEMS_MENU)

    def enter(self, cursor_pos):
        if (0 == cursor_pos):
            self._display.screen = MainScreen(self._display)
        else:
            if (1 == cursor_pos):
                self._display.screen = ManualPositionScreen(self._display)
            elif (2 == cursor_pos):
                self._display.screen = SecurityDistanceScreen(self._display)
            elif (3 == cursor_pos):
                self._display.screen = ModeSelectorScreen(self._display)
            elif (4 == cursor_pos):
                self._display.screen = VelocityStartScreen(self._display)
            elif (5 == cursor_pos):
                self._display.screen = VelocityStopScreen(self._display)


class ManualPositionScreen(ScreenBase):

    def __init__(self, display):
        super(ManualPositionScreen, self).__init__(display)
        # Load from item
        self._display.cursor_pos = sys.maxsize / 2

    def countItems(self) -> int:
        return sys.maxsize

    def display(self, draw):
        draw.text((1 , 1), "Move with Right/Left button.", fill=COLOR_PRIM_FONT, font=ImageFont.truetype(font_path, 12))

        y = 0.78 * LCD_HEIGHT
        draw.rectangle([0, y, LCD_WIDTH, LCD_HEIGHT], fill="white", outline="white")
        draw.text((0, 0.80 * LCD_HEIGHT), "enter to exit.", fill="black", font=ImageFont.truetype(font_path, 12))

    def enter(self, cursor_pos):
        self._display.screen = MenuScreen(self._display)


class SecurityDistanceScreen(ScreenBase):
    TITLE = "Security distance"
    value = 10

    def __init__(self, display):
        super(SecurityDistanceScreen, self).__init__(display)
        # Load from item
        self._display.cursor_pos = self.value

    def countItems(self) -> int:
        return 255

    def display(self, draw):
        self._display.createValue(draw, self.TITLE, self._display.getPos())

    def enter(self, cursor_pos):
        #  Save to item
        self._display.screen = MenuScreen(self._display)


class ModeSelectorScreen(ScreenBase):
    __TITLE = "Mode selector"
    __ITEMS = [
        ITEM_BACK,
        "OneWay",
        "TwoWay",
    ]

    def __init__(self, display):
        super(ModeSelectorScreen, self).__init__(display)
        # Load from item
        # self._display.cursor_pos = 0

    def countItems(self) -> int:
        return len(self.__ITEMS)

    def display(self, draw):
        self._display.createMenuScroll(draw, self.__ITEMS, "OneWay")

    def enter(self, cursor_pos):
        #  Save to item
        self._display.screen = MenuScreen(self._display)


class VelocityStartScreen(ScreenBase):
    TITLE = "Velocity Start"
    value = 10

    def __init__(self, display):
        super(VelocityStartScreen, self).__init__(display)
        # Load from item
        self._display.cursor_pos = self.value

    def countItems(self) -> int:
        return 255

    def display(self, draw):
        self._display.createValue(draw, self.TITLE, self._display.getPos())

    def enter(self, cursor_pos):
        #  Save to item
        self._display.screen = MenuScreen(self._display)


class VelocityStopScreen(ScreenBase):
    TITLE = "Velocity Stop"
    value = 10

    def __init__(self, display):
        super(VelocityStopScreen, self).__init__(display)
        # Load from item
        self._display.cursor_pos = self.value

    def countItems(self) -> int:
        return 255

    def display(self, draw):
        self._display.createValue(draw, self.TITLE, self._display.getPos())

    def enter(self, cursor_pos):
        #  Save to item
        self._display.screen = MenuScreen(self._display)

def get():
    k= click.getchar() #inkey()
    if k=='\x1b[A':
        return UP
    elif k=='\x1b[B':
        return DOWN
    elif k=='\x1b[C':
        return RIGHT
    elif k=='\x1b[D':
        return LEFT
    else:
        print("not an arrow key!\n")

def loop():
    t = threading.currentThread()
    if (mode == 1 or mode == 2):
        while getattr(t, "do_run", True):
            lcd.display()
            lcd.enter(get())
            # time.sleep(1)
    else:
        lcd.display()

        # Stop Screen 003
        lcd.enter(ENTER)
        lcd.display()

        # Play Screen
        lcd.enter(ENTER)

        # Menu Screen 004 & 005
        lcd.enter(RIGHT)
        lcd.display()
        lcd.enter(ENTER)
        lcd.display()

        # Manual postition 006 & 007
        lcd.enter(RIGHT)
        lcd.display()
        lcd.enter(ENTER)
        lcd.display()
        lcd.enter(ENTER)

        # Security distance 008 & 009
        lcd.enter(RIGHT)
        lcd.enter(RIGHT)
        lcd.display()
        lcd.enter(ENTER)
        lcd.display()
        lcd.enter(ENTER)

        # Mode Selector 010 & 011
        lcd.enter(RIGHT)
        lcd.enter(RIGHT)
        lcd.enter(RIGHT)
        lcd.display()
        lcd.enter(ENTER)
        lcd.display()
        lcd.enter(RIGHT)
        lcd.display()
        lcd.enter(ENTER)

        # Mode Velocity Start 012 & 013
        lcd.enter(RIGHT)
        lcd.enter(RIGHT)
        lcd.enter(RIGHT)
        lcd.enter(RIGHT)
        lcd.display()
        lcd.enter(ENTER)
        lcd.display()
        lcd.enter(ENTER)

        # Mode Velocity Stop 014 & 015
        lcd.enter(RIGHT)
        lcd.enter(RIGHT)
        lcd.enter(RIGHT)
        lcd.enter(RIGHT)
        lcd.enter(RIGHT)
        lcd.display()
        lcd.enter(ENTER)
        lcd.display()
        lcd.enter(ENTER)

if (LCD_MODE != 0):
    lcd = Lcd()
    lcd.boot()
    __displayLoop = threading.Thread(target=loop, name="display", args=(), daemon=True)
    time.sleep(2)
    __displayLoop.start()
