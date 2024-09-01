import os
import subprocess

from configuration.handler import get_data




def start():
    if get_data().gpu_manufacturer == "nvidia":
        start_nvidia_smi()
    elif get_data().gpu_manufacturer == "amd":
        start_rocm_smi()
    elif get_data().gpu_manufacturer == "intel":
        start_xpu_smi()

    if get_data().cpu_manufacturer == "nvidia":
        if get_data().cpu_collect_freq < 50:
            get_data().cpu_collect_freq = 50
        start_grace()
    elif get_data().cpu_manufacturer == "amd":
        start_perf()
    elif get_data().cpu_manufacturer == "intel":
        start_perf()
        

def stop():
    if get_data().gpu_manufacturer == "nvidia":
        stop_nvidia_smi()
    elif get_data().gpu_manufacturer == "amd":
        stop_rocm_smi()
    elif get_data().gpu_manufacturer == "intel":
        stop_xpu_smi()

    if get_data().cpu_manufacturer == "nvidia":
        stop_grace()
    elif get_data().cpu_manufacturer == "amd":
        stop_perf()
    elif get_data().cpu_manufacturer == "intel":
        stop_perf()




# GPU stats collection

def start_nvidia_smi():
    if not os.path.exists(get_data().gpu_output_filename):
        with open(get_data().gpu_output_filename, "w") as file:
            file.write(f"timestamp, name, uuid, pstate, memory.total [MiB], memory.used [MiB], memory.free [MiB], temperature.gpu, utilization.memory [%], utilization.gpu [%], power.management, power.draw [W]\n")

    command = ["nvidia-smi", "--format=csv,noheader,nounits", f"--loop-ms={get_data().gpu_collect_freq}", "--query-gpu=timestamp,name,uuid,pstate,memory.total,memory.used,memory.free,temperature.gpu,utilization.memory,utilization.gpu,power.management,power.draw"]
    with open(get_data().gpu_output_filename, "a+") as f:
        subprocess.Popen(command, stdout=f)

def stop_nvidia_smi():
    subprocess.run(["pkill", "nvidia-smi"])



# xpu-smi dump --ims 10 -d 0 -m 0,1,2,3,4,5,6,7,8,15,16,17,18,19,20 --file /tmp/gpu-stats.csv
def start_xpu_smi():
    command = ["xpu-smi", "dump", f"--ims {get_data().gpu_collect_freq}", "-d 0", "-m 0,1,2,3,4,5,6,7,8,15,16,17,18,19,20", "--file", str(get_data().gpu_output_filename)]
    subprocess.Popen(command)

def stop_xpu_smi():
    subprocess.run(["pkill", "xpu-smi"])



def start_rocm_smi():
    if not os.path.exists(get_data().gpu_output_filename):
        with open(get_data().gpu_output_filename, "w") as file:
            file.write(f"device,device_id,device_rev,unique_id,vbios_version,temp_edge_C,temp_junction_C,temp_memory_C,dcefclk_speed,dcefclk_level,fclk_speed,fclk_level,mclk_speed,fclk_level,sclk_speed,sclk_level,socclk_speed,socclk_level,pcie_level,performance_level,gpu_overdrive_percent,gpu_mem_overdrive_percent,max_power_W,avg_power_W,gpu_usage_percent,gpu_mem_usage_percent,mem_activity,avg_mem_bw,gpu_mem_vendor,pcie_replay,serial_num,voltage_mV,pci_bus,asd_fw_version,me_fw_version,mec_fw_version,mes_fw_version,mes_kiq_fw_version,pfp_fw_version,rlc_fw_version,sdma_fw_version,sdma2_fw_version,smc_fw_version,sos_fw_version,ta_ras_fw_version,vcn_fw_version,card_series,card_model,card_vendor,card_sku,energy_counter,accumulated_energy_uJ\n")

    command = [f"{get_data().autopilot_path}/hardware_stats/gpu/amd.py"]
    with open(get_data().gpu_output_filename, "a+") as f:
        subprocess.Popen(command, stdout=f)

def stop_rocm_smi():
    subprocess.run(["pkill", "-f", "amd.py"])




# CPU stats collection

def start_perf():
    command = ["perf", "stat", "-e", "power/energy-pkg/", "-x,", "-I", "0"]
    with open(get_data().cpu_output_filename, "w") as f:
        subprocess.Popen(command, stdout=f, stderr=f)

def stop_perf():
    subprocess.run(["pkill", "-SIGINT", "perf"])



def start_grace():
    command = [f"{get_data().autopilot_path}/hardware_stats/cpu/grace.py"]
    with open(get_data().cpu_output_filename, "w") as f:
        subprocess.Popen(command, stdout=f)

def stop_grace():
    subprocess.run(["pkill", "-SIGINT", "-f", "grace.py"])


