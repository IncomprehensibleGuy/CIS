from socket import socket, AF_INET, SOCK_STREAM
from os import system, remove, path, getpid


def communicate(host, port, message) -> str :
    ''' Helper-method to communicate repo_observer, dispatcher and test_runner
        :returns string response
    '''

    s = socket(AF_INET, SOCK_STREAM)
    s.connect((host, port))
    s.send(bytes(message, encoding='utf-8'))
    response = s.recv(1024).decode('utf-8')
    s.close()

    return response


module_process_ids = {} # Contains process id's of all dispatcher, pusher(if starter), all test runners


def write_process_id(module:str, identifier='', mode='w'):
    # To close module by pid
    pid = getpid()
    ids = open('ids.txt', mode)
    ids.write(module + identifier + ':' + str(pid) + '\n')
    ids.close()


def kill_process(id:str):
    try:
        system('taskkill -f /pid ' + id)
        return 0
    except:
        return -1


def kill_all_processes():
    for module, pid in module_process_ids.items():
        print('killing pid:' + pid)
        if not kill_process(pid):
            print(module + ' killed')
        else:
            print(module + ' still alive')


def get_all_processes_ids():
    ids = open('ids.txt', 'r')
    for line in ids.readlines():
        data = line.split(':')
        module_process_ids[data[0]] = data[1].strip('\n')
    ids.close()


def start_system(repository_path:str, test_every_commit:bool, n_test_runners:int):
    ''' Run CI system '''

    if path.exists(repository_path+'repo_clone_obs') and \
            path.exists(repository_path+'repo_clone_runner'):
        # Run dispatcher
        system('start cmd /K python ' + 'dispatcher.py')

        # Run pusher with flag 0 ()
        if test_every_commit:
            post_commit_file = open(repository_path + '.git/hooks/post-commit', 'w')
            code = open('post_commit_code.txt', 'r').read()
            post_commit_file.write(code)
            post_commit_file.close()
        else:
            if path.isfile(repository_path + '.git/hooks/post-commit'):
                remove(repository_path + '.git/hooks/post-commit')
            system('start cmd /K python ' + 'pusher.py' + ' 0')

        for n in range(n_test_runners):
            system('start cmd /K python ' + 'test_runner.py ' + repository_path + 'repo_clone_runner')


        import os,time
        time.sleep(2)
        get_all_processes_ids()
    else:
        print('no clones')