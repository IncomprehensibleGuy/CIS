if __name__ == "__main__":
    # Settings
    repo_path = 'C:/Users/Greg/Desktop/Projects/CIS/monitoring_repo/'
    if repo_path[-1] not in ['\\', '/']:
        repo_path += '/'

    repo_clone_runner_path = repo_path + 'repo_clone_runner'
    repo_clone_obs_path = repo_path + 'repo_clone_obs'

    test_results_path = ''

    observer_work = False # Determines whether observer will work or not

    n_test_runners = 1


    # Run CI system
    from os import system

    system('start cmd /K python ' + 'dispatcher.py')
    system('start cmd /K python ' + 'pusher.py ' + repo_clone_obs_path)

    if observer_work:
        pass
    else:
        # Create git hook script will run run_pusher.py
        pass

    for n in range(n_test_runners):
        system('start cmd /K python ' + 'test_runner.py ' + repo_clone_runner_path)