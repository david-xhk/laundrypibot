#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from laundrypiwasher import Washer
import RPi.GPIO as GPIO
import time


Washer.starting_time = 20
Washer.starting_threshold = 0.7
Washer.stopping_time = 30
Washer.stopping_threshold = 0.9
Washer.interval = 1


sensors = {24:1}


GPIO.setmode(GPIO.BCM)


for sensor, washer_id in sensors.items():
    GPIO.setup(sensor, GPIO.IN)
    sensors[sensor] = Washer(washer_id)


def main():
    while True:
        for sensor, washer in sensors.items():
            washer.step(GPIO.input(sensor) == GPIO.HIGH)
        time.sleep(Washer.interval)


if __name__ == "__main__":
    main()

