# Lights library for controlling LEDs on CASPR camera module.
from blinkt import set_brightness, set_pixel, clear, show
import time
from random import randint

# Blink a single LED with given color
def blink_color(index, interval, color):
    set_brightness(0.1)
    while True:
        clear()

        if color == 'red':
            set_pixel(index, 225, 0, 0)
        if color == 'green':
            set_pixel(index, 0, 128, 0)
        if color == 'yellow':
            set_pixel(index, 255, 100, 0)
        if color == 'blue':
            set_pixel(index, 0, 0, 255)

        show()
        time.sleep(interval)
        clear()
        show()
        time.sleep(interval)


# Rainbow of random colors across LED strip
def rand_rainbow():
    set_brightness(0.1)
    while True:
        for pixel in range(8):
            clear()
            r = randint(0, 255)
            g = randint(0, 255)
            b = randint(0, 255)

            set_pixel(pixel, r, g, b)
            show()
            time.sleep(0.05)

# Camera flash
def flash():
    set_brightness(1)
    for i in range(8):
        set_pixel(i, 255, 255, 255)
    show()
    return

# Set single LED without blinking
def set_led(index, color):
    set_brightness(0.1)
    
    if color == 'red':
        set_pixel(index, 255, 0, 0)
    if color == 'green':
        set_pixel(index, 0, 128, 0)
    if color == 'yellow':
        set_pixel(index, 255, 100, 0)
    if color == 'blue':
        set_pixel(index, 0, 0, 255)

    show()
    time.sleep(0.5)
    return

# Set all LEDs to one colors
def set_all(color):
    set_brightness(0.1)

    for i in range(8):
        if color == 'red':
            set_pixel(i, 255, 0, 0)
        if color == 'green':
            set_pixel(i, 0, 128, 0)
        if color == 'yellow':
            set_pixel(i, 255, 100, 0)
        if color == 'blue':
            set_pixel(i, 0, 0, 255)

    show()
    return

