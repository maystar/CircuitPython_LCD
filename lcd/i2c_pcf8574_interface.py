# Copyright (C) 2017 Dan Halbert
# Adapted from https://github.com/dbrgn/RPLCD, Copyright (C) 2013-2016 Danilo Bargen

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Low-level interface to PCF8574."""

import microcontroller
from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

from .pin_mapping import PinMapping


class I2CPCF8574Interface:
    class Pins:
        def __init__(self, en: int, rs: int, bl: int = const(0x00)):
            self.en = en
            self.rs = rs
            self.bl = bl

    _pins_of_mappings = {
        PinMapping.MAPPING1: Pins(const(0x04), const(0x01), const(0x08)),
        PinMapping.MAPPING2: Pins(const(0x80), const(0x10)),
    }

    def __init__(self, i2c, address, pin_mapping=PinMapping.MAPPING1):
        """
        CharLCD via PCF8574 I2C port expander.

        :param address: The I2C address of your LCD.
        """
        self.address = address
        self.pin_mapping = pin_mapping
        self.pins = self._pins_of_mappings[pin_mapping]

        self._backlight_pin_state = self.pins.bl

        self.i2c = i2c
        self.i2c_device = I2CDevice(self.i2c, self.address)
        self.data_buffer = bytearray(1)

    def deinit(self):
        self.i2c.deinit()

    @property
    def data_bus_mode(self):
        return const(0x00)  # LCD_4BITMODE

    @property
    def backlight(self):
        return self._backlight_pin_state == self.pins.bl

    @backlight.setter
    def backlight(self, value):
        self._backlight_pin_state = self.pins.bl if value else const(0x00)
        with self.i2c_device:
            self._i2c_write(self._backlight_pin_state)

    # Low level commands

    def send_instruction(self, value):
        self.send(value, const(0x00))

    def send_data(self, value):
        self.send(value, self.pins.rs)

    def send(self, value, rs_mode):
        """Send the specified value to the display in 4-bit nibbles.
        The rs_mode is either ``_RS_DATA`` or ``_RS_INSTRUCTION``."""
        data1 = (value & 0xF0) if self.pin_mapping == PinMapping.MAPPING1 else ((value >> 4) & 0x0F)
        data2 = ((value << 4) & 0xF0) if self.pin_mapping == PinMapping.MAPPING1 else (value & 0x0F)
        self._write4bits(rs_mode | data1 | self._backlight_pin_state)
        self._write4bits(rs_mode | data2 | self._backlight_pin_state)

    def _write4bits(self, value):
        """Pulse the `enable` flag to process value."""
        with self.i2c_device:
            self._i2c_write(value & ~self.pins.en)
            # This 1us delay is probably unnecessary, given the time needed
            # to execute the statements.
            microcontroller.delay_us(1)
            self._i2c_write(value | self.pins.en)
            microcontroller.delay_us(1)
            self._i2c_write(value & ~self.pins.en)
        # Wait for command to complete.
        microcontroller.delay_us(100)

    def _i2c_write(self, value):
        self.data_buffer[0] = value
        self.i2c_device.write(self.data_buffer)
