"""
For use with the CircuitPlayground Bluefruit. Polls the count of
local connectable devices and based on the count changes pixel colors.
"""

import time
import board
import neopixel
import analogio
import supervisor

from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement


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


def color_chase(color, wait):
    """
    Rotate through the neopixels setting the new color.
    """
    for i in range(10):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
    time.sleep(0.5)


def rainbow(wait=0.1):
    """
    Cycle through the RGB spectrum and set the new neopixel color.
    """
    for j in range(255):
        for i in range(len(pixels)):
            idx = int(i + j)
            pixels[i] = wheel(idx & 255)
        pixels.show()
        time.sleep(wait)


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
    print(
        "\ntotal: {total}\nconnectable: {found}\n".format(
            found=len(found), total=len(resp)
        )
    )
    return len(found)


light = analogio.AnalogIn(board.LIGHT)
ble = BLERadio()
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.2, auto_write=False)
pixels.fill((0, 0, 0))
pixels.show()

first_cycle = True

# Only want to scan a few times before idling
scan_count = 0

# For a "sleep" state we want to wake up to check
# the switch state.
sleeping = False
sleep_cycles = 0

while True:
    print(light.value)
    try:
        if int(light.value) > 300:
            while scan_count < 3:
                scan_count += 1
                found = local_scan()
                if found == 0 or found < 2:
                    color_chase(COLORS["OFF"], wait=0.5)
                if found > 0 and found < 5:
                    color_chase(COLORS["RED"], wait=0.5)
                if found >= 5:
                    color_chase(COLORS["BLUE"], wait=0.5)
                    color_chase(COLORS["PURPLE"], wait=0.5)
                time.sleep(5)
            # Stop scanning for 15 minutes
            sleeping = True
            # Sleeping for 5 minutes, but waking to check the
            # switch every minute.
            if sleep_cycles < 5:
                sleep_cycles += 1
                time.sleep(60)
            else:
                sleeping = False
                sleep_cycles = 0
                scan_count = 0
                rainbow()
                color_chase(COLORS["OFF"], wait=0.5)
        else:
            # It's dark lights out, clear all pixels
            color_chase(COLORS["OFF"], wait=0.5)
            first_cycle = True
            scan_count = 0
            sleeping = False
            sleep_cycles = 0

    except Exception:
        supervisor.reload()
