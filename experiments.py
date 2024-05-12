import os
import random
from itertools import product
import subprocess
import time




# Define experiment filenames
all_experiments_filename = 'combi.txt'
done_experiments_filename = 'expes.txt'

results_filename = "expe_results.csv"

gpu_id = "GPU-4ae69f76-868b-6458-0121-008176bcd866"
gpu_output_filename = "gpu_power.csv"

cooldown_time = 60 # Time in seconds

# Define experiment parameters
versions = ['version1', 'version2', 'version3', 'version4']
sizes = [216, 408, 600, 792]
times = [0.2, 1, 2]
repeats = [1, 2, 3]




def create_randomized():
    if not os.path.exists(all_experiments_filename):
        # Generate all possible combinations
        all_experiments = list(product(versions, sizes, times, repeats))

        # Shuffle the combinations randomly
        random.shuffle(all_experiments)

        with open(all_experiments_filename, 'w') as file:
            for combination in all_experiments:
                line = ', '.join(map(str, combination))  # Convert each element to a string
                file.write(f"{line}\n")
            
        # print(all_experiments)



def read(filename, data):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for line in file:
                elements = []
                for x in line.strip().split(', '):
                    if isinstance(x, str):
                        elements.append(str(x))
                    else:
                        if '.' in x:
                            elements.append(float(x))
                        else:
                            elements.append(int(x))
                data.append(tuple(elements))
    else:
        data = []



def checkpoint(data):
    with open(done_experiments_filename, 'a+') as file:
        line = ', '.join(map(str, data))
        file.write(f"{line}\n")



def cooldown():
    time.sleep(cooldown_time)



def clean_temporary_files():
    subprocess.run(["find", "/path/to/folder", "-name", "*.rsf*", "-delete"])



def start_nvidia_smi():
    if not os.path.exists(gpu_output_filename):
        with open(gpu_output_filename, "w") as file:
            file.write(f"timestamp, name, uuid, pstate, memory.total [MiB], memory.used [MiB], memory.free [MiB], temperature.gpu, utilization.memory [%], utilization.gpu [%], power.management, power.draw [W]\n")

    command = ["nvidia-smi", "--id", str(gpu_id), "--format=csv,noheader,nounits", "--loop-ms=100", "--query-gpu=timestamp,name,uuid,pstate,memory.total,memory.used,memory.free,temperature.gpu,utilization.memory,utilization.gpu,power.management,power.draw"]
    with open(gpu_output_filename, "a+") as f:
        subprocess.Popen(command, stdout=f)



def stop_nvidia_smi():
    subprocess.run(["pkill", "nvidia-smi"])



# Function to run an experiment
def run(experiment):
    expe_version = experiment[0]
    expe_size = experiment[1]
    expe_time = experiment[2]
    
    try:
        print(f"/path/to/{expe_version}/executable {expe_size} {expe_time}")

        command = f"perf stat -e power/energy-pkg/ -x, -o cpu_power.csv /path/to/{expe_version}/executable {expe_size} {expe_time}"

        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = process.communicate()

        # Extract relevant data
        output = output.decode("utf-8")
        output = next((line for line in output.split('\n') if line.startswith(str(expe_version))), None)

        joules = subprocess.check_output(["tail", "-n", "+3", "cpu_power.csv"]).decode("utf-8")
        joules = joules.strip().split(',')[0]

        # Combine output
        output += f",{joules}"

        with open(f"{results_filename}", "a+") as f:
            f.write(output + "\n")  # Write joules in the same line

        print(f"{output}")
    except KeyboardInterrupt:
        # If Ctrl+C is pressed during experiments, stop nvidia-smi
        stop_nvidia_smi()
        clean_temporary_files()
        raise





