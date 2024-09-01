import os
import yaml
import argparse

from .yaml_to_dot import Config



_data = None



def parse_args():
    global args
    parser = argparse.ArgumentParser(description='Experimentation autopilot.')
    parser.add_argument('--config_file_path', type=str, help='Path to the configuration file.')
    args = parser.parse_args()

    if args.config_file_path:
        read_config_file(args.config_file_path)
    else:
        read_config_file(os.path.join(os.path.dirname(__file__), 'config.yaml'))
    
    update_config()



def read_config_file(config_file_path):
    global _data

    with open(config_file_path, 'r') as file:
        config_dict = yaml.safe_load(file)

    _data = Config(config_dict)

    print(f"Project name: {_data.project_name}, cooldown time: {_data.cooldown_time}")



def update_config():
    """ Updates the configuration _data by setting the necessary file paths based on the current configuration. """

    global _data
    if _data is not None: 
        _data.autopilot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
        _data.all_experiments_filename = os.path.join(_data.experiment_folder_name, _data.all_experiments_filename)
        _data.done_experiments_filename = os.path.join(_data.experiment_folder_name, _data.done_experiments_filename)
        _data.results_filename = os.path.join(_data.experiment_folder_name, _data.results_filename)
        _data.cpu_output_filename = os.path.join(_data.experiment_folder_name, _data.cpu_output_filename)
        _data.gpu_output_filename = os.path.join(_data.experiment_folder_name, _data.gpu_output_filename)
    else:
        raise ValueError("_Data has not been initialized. Please call parse_args() or read_config_file() first.")



def get_data():
    """ Returns the _data variable. Raises an error if it's not initialized. """
    global _data
    if _data is None:
        raise ValueError("_Data is not initialized. Please call parse_args() or read_config_file() first.")
    return _data








# tmp = {
#     'all_experiments_filename': '',
#     'done_experiments_filename': '',
#     'results_filename': '',
#     'cpu_output_filename': '',
#     'gpu_output_filename': ''
# }

