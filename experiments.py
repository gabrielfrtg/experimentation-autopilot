import os
import random
from itertools import product
import subprocess
import time

from configuration.handler import get_data
import hardware_stats.collector as hardware_stats_collector
from sbatch.launcher import initialize_sbatch, launch_job



def create_experiment_folder():
    if not os.path.exists(get_data().experiment_folder_name):
        os.makedirs(get_data().experiment_folder_name)



def create_randomized():
    if not os.path.exists(get_data().all_experiments_filename):
        # Generate all possible combinations
        all_experiments = list(product(get_data().versions, get_data().sizes, get_data().times, get_data().repeats))

        # Shuffle the combinations randomly
        random.shuffle(all_experiments)

        with open(get_data().all_experiments_filename, 'w') as file:
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
    with open(get_data().done_experiments_filename, 'a+') as file:
        line = ', '.join(map(str, data))
        file.write(f"{line}\n")



def cooldown():
    if not get_data().use_slurm:
        time.sleep(get_data().cooldown_time)



def clean_temporary_files():
    for extension in get_data().temp_file_extensions:
        subprocess.run(["find", get_data().project_path, "-iname", f"*.{extension}*", "-delete"])



# Function to run an experiment
def run(experiment):
    expe_version = experiment[0]
    expe_size = experiment[1]
    expe_time = experiment[2]
    
    try:
        print(f"Running {get_data().project_path}/{expe_version}/{get_data().project_executable} with size {expe_size} and simulation time {expe_time}...")

        command = f"{get_data().project_path}/{expe_version}/{get_data().project_executable} TTI {expe_size} {expe_size} {expe_size} 16 12.5 12.5 12.5 0.001 {expe_time}"
        print(command)

        if get_data().use_slurm:
            initialize_sbatch(command, expe_version)
            launch_job()
        else:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ.copy())
            output, _ = process.communicate()

            # Stop hardware stats collector to get the final stats
            hardware_stats_collector.stop()

            # Extract only the CSV formated line with experimental data
            output = output.decode("utf-8")
            output = next((line for line in output.split('\n') if line.startswith(str(expe_version))), None)

            joules = subprocess.check_output(["head", "-n", "1", f"{get_data().cpu_output_filename}"]).decode("utf-8")
            joules = joules.strip().split(',')[0]

            # Combine output
            if output is not None:
                output += f",{joules}"
            else:
                output = f"{expe_version},TTI,{expe_size},{expe_size},{expe_size},16,12.5,12.5,12.5,0.001,{expe_time},,,,,,{joules}"

            with open(f"{get_data().results_filename}", "a+") as f:
                f.write(output + "\n")  # Write joules in the same line

            print(f"{output}")
    except KeyboardInterrupt:
        # If Ctrl+C is pressed during experiments, stop hardware stats collector and clean temporary files
        hardware_stats_collector.stop()
        clean_temporary_files()
        raise





