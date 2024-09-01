#!/usr/bin/env python3

import signal
import sys
import time

# from configuration.handler import get_data



total_energy_consumed = 0.0



def handle_sigint(signum, frame):
    print(f"{total_energy_consumed},")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)



while True:
    try:
        power_0 = float(open('/sys/class/hwmon/hwmon3/device/power1_average').read())
        power_1 = float(open('/sys/class/hwmon/hwmon6/device/power1_average').read())

        energy_0 = power_0 * 0.05 / 1000000
        energy_1 = power_1 * 0.05 / 1000000

        total_power = power_0 + power_1
        total_energy = energy_0 + energy_1

        # print(f"grace,{power_0},{power_1},{energy_0},{energy_1},{total_power},{total_energy}")

        total_energy_consumed += total_energy

        # TODO: get from the configuration file
        time.sleep(50 / 1000)
    except KeyboardInterrupt:
        pass
