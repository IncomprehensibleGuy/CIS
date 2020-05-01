if __name__ == "__main__":
    from os import system


    # Settings
    repo_path = 'C:/Users/Greg/Desktop/Projects/CIS/monitoring_repo/'
    repo_clone_runner_path = repo_path + 'repo_clone_runner'
    repo_clone_obs_path = repo_path + 'repo_clone_obs'

    n_test_runners = 1

    start_dispatcher_command = 'dispatcher.py'
    start_test_runner_command = 'test_runner.py ' + repo_clone_runner_path
    start_repo_observer_command = 'repo_observer.py ' + repo_clone_obs_path


    # Run CIS
    system('start cmd /K python ' + start_dispatcher_command)
    #system('start cmd /K python ' + start_repo_observer_command)
    for n in range(n_test_runners):
        system('start cmd /K python ' + start_test_runner_command)