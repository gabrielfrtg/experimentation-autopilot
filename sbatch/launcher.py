import subprocess

from configuration.handler import get_data



def initialize_sbatch(command, version):
    sbatch_script = f"""#!/bin/bash
#SBATCH --job-name={get_data().project_name}
#SBATCH --output={get_data().experiment_folder_name}/slurm_output/{get_data().project_name}_%j.out
#SBATCH --error={get_data().experiment_folder_name}/slurm_output/{get_data().project_name}_%j.err
#SBATCH --partition={get_data().slurm_settings.partition}
#SBATCH --nodelist={get_data().slurm_settings.node_list}
#SBATCH --nodes={get_data().slurm_settings.num_nodes}\n\n"""

    if get_data().gpu_manufacturer == "nvidia":
        sbatch_script += f"""nvidia-smi --format=csv,noheader,nounits --loop-ms={get_data().gpu_collect_freq} --query-gpu=timestamp,name,uuid,pstate,memory.total,memory.used,memory.free,temperature.gpu,utilization.memory,utilization.gpu,power.management,power.draw >> {get_data().gpu_output_filename} &\n\n"""
    elif get_data().gpu_manufacturer == "amd":
        sbatch_script += f"""{get_data().autopilot_path}/hardware_stats/gpu/amd.py >> {get_data().gpu_output_filename} &\n\n"""
    elif get_data().gpu_manufacturer == "intel":
        sbatch_script += f"""xpu-smi dump --ims {get_data().gpu_collect_freq} -m 0,1,2,3,4,5,6,7,8,15,16,17,18,19,20 --file {get_data().gpu_output_filename} &\n\n"""

    if get_data().cpu_manufacturer == "amd" or get_data().cpu_manufacturer == "intel":
        sbatch_script += f"""output=$(perf stat -e power/energy-pkg/ -x, -o {get_data().cpu_output_filename} {command})\n\n"""
    elif get_data().cpu_manufacturer == "nvidia":
        sbatch_script += f"""{get_data().autopilot_path}/hardware_stats/cpu/grace.py > {get_data().cpu_output_filename} &\n\n"""
        sbatch_script += f"""output=$({command})\n\n"""
        sbatch_script += f"""pkill -SIGINT -f "grace.py"\n\n"""

    if get_data().cpu_manufacturer == "nvidia":
        sbatch_script += f"""first_line=$(sed -n '1p' "{get_data().cpu_output_filename}")
joules=$(echo $first_line | tr -d '[:space:]' | cut -d',' -f1)\n\n"""
    else:
        sbatch_script += f"""first_line=$(sed -n '3p' "{get_data().cpu_output_filename}")
joules=$(echo $first_line | tr -d '[:space:]' | cut -d',' -f1)\n\n"""

    sbatch_script += f"""matched_line=$(echo "$output" | grep "^{version}")
if [ -z "$matched_line" ]; then
    echo "failed,$joules"
else
    echo "$matched_line,$joules" >> {get_data().results_filename}
fi\n\n"""


    with open(f"{get_data().project_name}.sbatch", 'w') as file:
        file.write(sbatch_script)



def launch_job():
    result = subprocess.run(['sbatch', f"{get_data().project_name}.sbatch"], stdout=subprocess.PIPE, text=True)

    print(result.stdout)


