import experiments



experiments.create_randomized()



all_experiments = []
experiments.read(experiments.all_experiments_filename, all_experiments)

done_experiments = []
experiments.read(experiments.done_experiments_filename, done_experiments)

# Find experiments to perform (not done yet) OBS: order in all_experiments is not preserved
remaining_experiments = [exp for exp in all_experiments if exp not in done_experiments]



print(all_experiments)
print(remaining_experiments)


total_expes_count = len(all_experiments)
done_expes_count = len(done_experiments)


try:
    for experiment in remaining_experiments:
        print(f"Running experiment {done_expes_count+1}/{total_expes_count}...")

        experiments.start_nvidia_smi()

        experiments.run(experiment)
        
        experiments.checkpoint((experiment))

        experiments.stop_nvidia_smi()

        done_expes_count+=1

        print(f"Experiment {done_expes_count} done!")

        experiments.clean_temporary_files()

        print(f"Cooling down...")

        experiments.cooldown()
finally:
    experiments.stop_nvidia_smi()
    experiments.clean_temporary_files()





