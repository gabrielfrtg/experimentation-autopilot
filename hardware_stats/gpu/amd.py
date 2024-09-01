#!/usr/bin/env python3

import subprocess
import time

# from configuration import handler as config

while True:
    command = ["rocm-smi", "-a", "--csv"]
    result = subprocess.run(command, capture_output=True, text=True)
    filtered_output = "\n".join([line for line in result.stdout.splitlines() if line.startswith("card")])
    print(filtered_output, flush=True)
    
    time.sleep(100 / 1000)