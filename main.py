if __name__ == "__main__":
    import os


    # Settings
    repo_path = 'C:/Users/Greg/Desktop/Projects/CIS/monitoring_repo/'
    repo_clone_runner_path = repo_path + 'repo_clone_runner'

    n_test_runners = 1

    start_dispatcher_command = 'dispatcher.py'
    start_test_runner_command = 'test_runner.py ' + repo_clone_runner_path


    # Run system
    os.system('start cmd /K python ' + start_dispatcher_command)
    for n in range(n_test_runners):
        os.system('start cmd /K python ' + start_test_runner_command)