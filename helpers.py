from socket import socket, AF_INET, SOCK_STREAM
from os import system, remove, path, pardir, getpid
import subprocess


def communicate(host:str, port:int, message:str) -> str :
    ''' Helper-method to communicate repo_observer, dispatcher and test_runner
        :returns string response
    '''

    endpoint = socket(AF_INET, SOCK_STREAM)
    endpoint.connect((host, port))
    endpoint.send(bytes(message, encoding='utf-8'))
    response = endpoint.recv(1024).decode('utf-8')
    endpoint.close()

    return response


module_process_ids = {} # Contains process id's of all dispatcher, pusher(if starter), all test runners


def write_process_id(module:str, identifier='', mode='w'):
    ''' Write process id's to a file to stop modules '''
    pid = getpid()
    ids = open('ids.txt', mode)
    ids.write(module + identifier + ':' + str(pid) + '\n')
    ids.close()


def kill_process(id:str):
    '''
    :returns 0 if successfully stop process, else -1
    '''
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

    # Create repo clones for pusher and test_runner
    if ( not path.exists(repository_path + 'repo_clone_pusher') ) and \
            ( not path.exists(repository_path + 'repo_clone_test_runner') ):
        subprocess.check_output(['clone_repo.sh', repository_path], shell=True)

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

    # Run test runner('s)
    for n in range(n_test_runners):
        system('start cmd /K python ' + 'test_runner.py ' + repository_path + 'repo_clone_runner')

    import os, time
    time.sleep(2)
    get_all_processes_ids()