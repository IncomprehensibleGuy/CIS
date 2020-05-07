from os import system, remove, path


settings = {
    'repository_path':'',
    'repo_clone_observer_path': '',
    'repo_clone_test_runner_path':'',
    'test_results_path':'',
    'test_every_commit':True, # Determines whether we will test every commit or check repo periodically
    'n_test_runners': 1,
}

module_process_ids = {}


def kill_process(id: str):
    try:
        system('taskkill -f /pid ' + id)
        return 0
    except:
        return -1


def kill_all():
    for module, pid in module_process_ids.items():
        print('killing pid:' + pid)
        if not kill_process(pid):
            print(module + ' killed')
        else:
            print(module + ' still alive')


def get_ids():
    ids = open('ids.txt', 'r')
    for line in ids.readlines():
        data = line.split(':')
        module_process_ids[data[0]] = data[1].strip('\n')
        print('got ' + data[0] + ' pid: ' + data[1].strip('\n'))
    ids.close()


def start_system(repository_path:str):
    settings['repository_path'] = repository_path
    settings['repo_clone_observer_path'] = repository_path + 'repo_clone_obs'
    settings['repo_clone_test_runner_path'] = repository_path + 'repo_clone_runner'

    # Run CI system
    system('start cmd /K python ' + 'dispatcher.py')

    if settings['test_every_commit']:
        post_commit_file = open(settings['repository_path'] + '.git/hooks/post-commit', 'w')
        code = open('post_commit_code.txt', 'r').read()
        post_commit_file.write(code)
        post_commit_file.close()
    else:
        if path.isfile(settings['repository_path'] + '.git/hooks/post-commit'):
            remove(settings['repository_path'] + '.git/hooks/post-commit')
        system('start cmd /K python ' + 'pusher.py' + ' 0')

    for n in range(settings['n_test_runners']):
        system('start cmd /K python ' + 'test_runner.py ' + settings['repo_clone_test_runner_path'])


    import os,time
    time.sleep(2)
    get_ids()
