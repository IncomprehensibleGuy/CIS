import os


def main():
    repo_clone_runner_path = 'C:/Users/Greg/Desktop/Projects/CIS/monitoring_repo/repo_clone_runner'
    repo_clone_obs_path = 'C:/Users/Greg/Desktop/Projects/CIS/monitoring_repo/repo_clone_obs'

    start_dispatcher_command = 'dispatcher.py'
    start_test_runner_command = 'test_runner.py ' + repo_clone_runner_path
    start_repo_observer_command = 'repo_observer.py ' + repo_clone_obs_path

    os.system('start cmd /K python ' + start_dispatcher_command)
    os.system('start cmd /K python ' + start_repo_observer_command)
    os.system('start cmd /K python ' + start_test_runner_command)


if __name__ == "__main__":
    main()