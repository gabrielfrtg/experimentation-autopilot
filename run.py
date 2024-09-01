import experiments
from configuration.handler import parse_args, get_data
from hardware_stats import collector as hardware_stats_collector



if __name__ == "__main__":
    parse_args()

    experiments.create_experiment_folder()

    experiments.create_randomized()



    all_experiments = []
    experiments.read(get_data().all_experiments_filename, all_experiments)

    done_experiments = []
    experiments.read(get_data().done_experiments_filename, done_experiments)

    # Find experiments to perform (not done yet) OBS: order in all_experiments is not preserved
    remaining_experiments = [exp for exp in all_experiments if exp not in done_experiments]



    print(all_experiments)
    print(remaining_experiments)


    total_expes_count = len(all_experiments)
    done_expes_count = len(done_experiments)


    try:
        for experiment in remaining_experiments:
            print(f"Running experiment {done_expes_count+1}/{total_expes_count}...")

            hardware_stats_collector.start()

            experiments.run(experiment)
            
            experiments.checkpoint((experiment))

            hardware_stats_collector.stop()

            done_expes_count+=1

            print(f"Experiment {done_expes_count} done!")

            experiments.clean_temporary_files()

            print(f"Cooling down...")

            experiments.cooldown()
    finally:
        hardware_stats_collector.stop()
        experiments.clean_temporary_files()





