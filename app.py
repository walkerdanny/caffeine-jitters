import app
import time
import asyncio
from .adafruit_drv2605 import *
from machine import Pin, I2C
from events.input import Buttons, BUTTON_TYPES, ButtonDownEvent, ButtonUpEvent
from system.eventbus import eventbus
from system.hexpansion.util import read_hexpansion_header, get_hexpansion_block_devices, detect_eeprom_addr
from system.hexpansion.events import HexpansionRemovalEvent, HexpansionInsertionEvent
from system.hexpansion.config import *
from app_components import clear_background
from random import randint
import tildagonos


class CaffeineJitter(app.App):
    def __init__(self):
        self.button_states = Buttons(self)
        self.app = app
        self.jitter_factor = 0.5 # Litres of Club Mate consumed
        self.amount_consumed_col = [1.0, 1.0, 1.0] # This is just the colour of the text
        self.jitter_timeout_ms = self.generate_timeout() # How long between jitters
        self.last_jitter_time = time.ticks_ms() # Last time we did a jitter in ms
        self.cool_drv2605_effects = [92, 47, 58, 85, 82] # Add whatever you want here, get weird with it. Don't play the continious ones though. This is literally just a list of effect numbers I thought were fun and aggressive enough to be felt.

        self.hexpansion_config = self.scan_for_hexpansion()
        if self.hexpansion_config is not None:
            self.drv = DRV2605(self.hexpansion_config.i2c)
            self.enable_pin = self.hexpansion_config.pin[3] # This is the enable pin! Drive it high to enable the driver IC! Don't be like me and forget to do this!
            self.enable_pin.init(self.enable_pin.OUT)
            self.enable_pin.on()
        else:
            self.drv = None
            self.enable_pin = None
        eventbus.on(ButtonDownEvent, self._handle_buttondown, self)
        eventbus.on_async(HexpansionInsertionEvent, self.handle_hexpansion_insertion, self)
        eventbus.on_async(HexpansionRemovalEvent, self.handle_hexpansion_removal, self)


    def handle_hexpansion_insertion(self):
        self.hexpansion_config = self.scan_for_hexpansion()

    def handle_hexpansion_removal(self):
        self.hexpansion_config = self.scan_for_hexpansion()


    def scan_for_hexpansion(self): # Is there a proper way of doing this so I don't have to implement it myself?
        for port in range(1, 7):
            print(f"Searching for hexpansion on port: {port}")
            i2c = I2C(port)
            addr = detect_eeprom_addr(i2c)

            if addr is None:
                continue
            else:
                print("Found EEPROM at addr " + hex(addr))

            header = read_hexpansion_header(i2c, addr)
            if header is None:
                continue
            else:
                print("Read header: " + str(header))

            if (header.vid is 0xCAFE) and (header.pid is 0xCAFF):
                # We found it, the search is over!
                print("Found the desired hexpansion in port " + str(port))
                return HexpansionConfig(port)
        
        return None

    def _handle_buttondown(self, event: ButtonDownEvent):
        if BUTTON_TYPES["CANCEL"] in event.button:
            self._cleanup()
            self.minimise()
        
        if BUTTON_TYPES["UP"] in event.button:
            self._cleanup()
            self.jitter_factor += 0.1   
            if self.jitter_factor >= 1:
                self.jitter_factor = 1.0
            self.jitter_timeout_ms = self.generate_timeout() # Update the timeout whenever the amount consumed has changed
        
        if BUTTON_TYPES["DOWN"] in event.button:
            self._cleanup()
            self.jitter_factor -= 0.1
            if self.jitter_factor < 0:
                self.jitter_factor = 0.0
            self.jitter_timeout_ms = self.generate_timeout() # Update the timeout whenever the amount consumed has changed



    def _cleanup(self):
        eventbus.remove(ButtonDownEvent, self._handle_buttondown, self.app)

    def update(self, delta):
        if self.hexpansion_config is not None:
            self.jitter_randomly()

    def draw(self, ctx):
        if self.hexpansion_config is None:
            clear_background(ctx)
            ctx.font_size = 24

            wi = ctx.text_width("No hexpansion detected")
            ctx.rgb(1.0,1.0,1.0).move_to(-wi/2,0).text("No hexpansion detected")
        else:
            clear_background(ctx)
            ctx.font_size = 24

            wi = ctx.text_width("Club mate consumed:")
            ctx.rgb(1.0,1.0,1.0).move_to(-wi/2,-30).text("Club mate consumed:")

            ctx.font_size = 40
            amount_consumed_text = '%.1f' %self.jitter_factor + " litres"
            amount_consumed_width = ctx.text_width(amount_consumed_text)

            # Make the text increasingly red by turning down the green and blue as the jitter factor increases
            self.amount_consumed_col[1] = 1.0 - self.jitter_factor
            self.amount_consumed_col[2] = 1.0- self.jitter_factor

            ctx.rgb(self.amount_consumed_col[0],self.amount_consumed_col[1], self.amount_consumed_col[2]).move_to(-amount_consumed_width/2, 12).text(amount_consumed_text)


    def jitter_randomly(self):
        if self.jitter_factor >= 0.1:
            print("Next jitter in: " + str( -(time.ticks_ms()-self.last_jitter_time - self.jitter_timeout_ms)) + "ms")
            if (time.ticks_ms() - self.last_jitter_time) > self.jitter_timeout_ms:            
                self.do_one_jitter()
                self.last_jitter_time = time.ticks_ms()
                self.jitter_timeout_ms = self.generate_timeout()
                    # Gives a range of 1-6 seconds when jf is 1
                    # Give a range  of 10-60 seconds when jf is 0.1


    def generate_timeout(self):
        return (1 -(self.jitter_factor**2)) * 2000 * randint(4,8)


    def do_one_jitter(self):
        print("Jittering")
        effect_choice = randint(0,len(self.cool_drv2605_effects)-1)
        self.drv.sequence[0] = Effect(self.cool_drv2605_effects[effect_choice])  # Set the effect on slot 0.
        self.drv.play() # Note that we never call stop! This means if you use the continous effects it won't stop buzzing until the next effect plays


__app_export__ = CaffeineJitter

