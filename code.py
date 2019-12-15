"""
For use with the CircuitPlayground Bluefruit. Polls for a ble connection
with an Apple device. Once paired checks for new SMS notifications that
contain a valid color. If a valid color is provided the playground neopixels
are set. If a connection is not detected within 15 minutes the playground will
enter a temporary sleep and restart the cycle.
"""

import time
import board
import neopixel
import adafruit_ble
from adafruit_ble.advertising.standard import SolicitServicesAdvertisement
from adafruit_ble.services.apple import AppleNotificationService

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
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
    time.sleep(0.5)

def rainbow(wait=.1):
    """
    Cycle through the RGB spectrum and set the new neopixel color.
    """
    for j in range(255):
        for i in range(len(pixels)):
            idx = int(i + j)
            pixels[i] = wheel(idx & 255)
        pixels.show()
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

radio = adafruit_ble.BLERadio()
a = SolicitServicesAdvertisement()
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.1, auto_write=True)

a.solicited_services.append(AppleNotificationService)
radio.start_advertising(a)

known_notifications = set()
found_color_count = 0
sleeping = 0

while not radio.connected:
    """
    If we are not connected sleep for 6 seconds unless
    it's been 15 minutes. After 15 minutes do a rainbow
    cycle and go to sleep for 5 minutes.
    """
    color_chase(COLORS["OFF"], wait=.5)
    if sleeping == 150:
        rainbow()
        time.sleep(300)
        sleeping == 0
    time.sleep(6)
    sleeping += 1
    pass

while radio.connected:
    """
    Check for SMS notifications on the paired device and set
    the color of the neopixels on the circuitplayground if a
    valid color is provided.
    """
    for connection in radio.connections:
        if not connection.paired:
            connection.pair()
            sleeping = 0

        ans = connection[AppleNotificationService]

        for notification in ans.wait_for_new_notifications():
            if notification.app_id == "com.apple.MobileSMS"and not notification.preexisting:
                if notification.message.upper() in COLORS.keys():
                    if found_color_count == 2:
                        rainbow(.01)
                        found_color_count = 0
                    color_chase(COLORS[notification.message.upper()], wait=.5)
                    found_color_count += 1

    time.sleep(1)

