import time
from random import randint
from blinkt import set_pixel, set_brightness, show, clear


while True:
    for pixel in range(8):
        clear()

        r = randint(0,255)

        g = randint(0,255)

        b = randint(0,255)

        set_pixel(pixel, r, g, b)
        show()
        time.sleep(0.05)
