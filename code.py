"""
For use with the CircuitPlayground Bluefruit. Polls the count of
local connectable devices and based on the count changes pixel colors.
"""

import time

import adafruit_ble
from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_circuitplayground.bluefruit import cpb

# NEOPIXEL RGB values
COLORS = {
    "RED": (255, 0, 0),
    "YELLOW": (255, 150, 0),
    "GREEN": (0, 255, 0),
    "CYAN": (0, 255, 255),
    "BLUE": (0, 0, 255),
    "PURPLE": (180, 0, 255),
    "WHITE": (255, 255, 255),
    "ORANGE": (255, 165, 0),
    "PINK": (255, 192, 203),
    "OFF": (0, 0, 0),
}

def color_chase(color, wait):
    """
    Rotate through the neopixels setting the new color.
    """
    for i in range(10):
        cpb.pixels[i] = color
        time.sleep(wait)
    time.sleep(0.5)

def rainbow(wait=.1):
    """
    Cycle through the RGB spectrum and set the new neopixel color.
    """
    for j in range(255):
        for i in range(len(cpb.pixels)):
            idx = int(i + j)
            cpb.pixels[i] = wheel(idx & 255)
        time.sleep(wait)

def wheel(pos):
    """
    Pick circuitplayground neopixel index.
    """
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def local_scan(timeout=2):
    """
    Find out how many devices are in the area that we can
    connect to.
    """
    print("\nscanning\n")
    found = set()
    resp = set()

    for ad in ble.start_scan(Advertisement, timeout=timeout):
        # dir(ad)
        # ['__bytes__', '__class__', '__dict__', '__init__', '__len__',
        # '__module__', '__qualname__', '__repr__', '__str__', 'address',
        # 'connectable', 'matches', 'rssi', 'scan_response', 'tx_power',
        # 'complete_name', 'from_entry', 'prefix', 'data_dict', 'flags',
        # 'mutable', 'short_name', 'appearance', '_rssi']
        #
        # Most of the name related fields just return None
        resp.add(ad.address)
        if ad.connectable:
            print(ad.__dict__)
            found.add(ad.address)

    print("\nscan done\n")
    print("\ntotal: {total}\nconnectable: {found}\n".format(found=len(found), total=len(resp)))
    return len(found)

ble = BLERadio()
cpb.pixels.brightness = 0.1
FIRST = True
scan_count = 0

def deep_sleep(seconds):
    """
    Would be useful to be able to power down the radio
    to save battery, but for now this is a wrapper
    to indicate behavior to the reader.
    """
    print("\nGoing to sleep for {} seconds.\n".format(seconds))
    time.sleep(seconds)


while True:
    if cpb.switch:
        if FIRST:
            rainbow(.01)
            FIRST = False
        while scan_count < 2:
            scan_count += 1
            found = local_scan()
            if found == 0 or found < 2:
                color_chase(COLORS["OFF"], wait=.5)
            if found > 0 and found < 5:
                color_chase(COLORS['RED'], wait=.5)
            if found >= 5:
                color_chase(COLORS['BLUE'], wait=.5)
                color_chase(COLORS['PURPLE'], wait=.5)
            time.sleep(5)
        # Stop scanning for 15 minutes
        deep_sleep(900)
        scan_count = 0
    else:
        # Slide is off clear all pixels
        color_chase(COLORS["OFF"], wait=.5)
        FIRST = True
        scan_count = 0
