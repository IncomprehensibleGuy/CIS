import os
import argparse
import subprocess
from time import sleep
from socket import error

import helpers


def make_commit_id_file(repo_clone_pusher:str):
    '''
    Call the bash script that will update the repo and check for changes.
    If there's a change, it will drop a .commit_id file with the latest commit in the current working directory.
    '''
    try:
        subprocess.check_output(['update_repo.sh', repo_clone_pusher], shell=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f'Could not update and check repository. Reason: {e.output}')


def get_commit_from_file() -> str:
    if os.path.isfile('.commit_id'):
        commit_file = open('.commit_id', 'r')
        commit = commit_file.readline()
        commit_file.close()
        return commit
    else:
        return 'not commit'


def push_commit_to_dispatcher(dispatcher_host:str, dispatcher_port:int, commit:str):
    '''
    Check the status of the dispatcher server to see if we can send the commit and if everything is ok send it.
    '''
    try:
        response = helpers.communicate(dispatcher_host, dispatcher_port, 'status')
    except error:
        raise Exception(f'Could not communicate with dispatcher server: {error}')

    if response == 'OK':
        response = helpers.communicate(dispatcher_host, dispatcher_port, 'dispatch:'+commit)
        if response == 'OK':
            print('commit dispatched')
        else:
            raise Exception(f'Could not dispatch the test: {response}')
    else:
        raise Exception(f'Could not dispatch the test: {response}')


def main_job(repo_clone_pusher:str, dispatcher_host:str, dispatcher_port:int):
    make_commit_id_file(repo_clone_pusher)
    commit = get_commit_from_file()
    if commit != 'not commit':
        # We have a change -> send the commit to dispatcher
        push_commit_to_dispatcher(dispatcher_host, dispatcher_port, commit)
    else:
        print('no .commit_id file')


def observe(repo_clone_pusher:str, dispatcher_host:str, dispatcher_port:int, schedule:int):
    while True:
        main_job(repo_clone_pusher, dispatcher_host, dispatcher_port)
        sleep(schedule)


if __name__ == '__main__':
    # To close pusher
    helpers.write_process_id('pusher', mode='a')

    # Determines whether we will check repo periodically (0) or test every commit (1)
    parser = argparse.ArgumentParser()
    parser.add_argument('repo_path', type=str, action='store')
    parser.add_argument('test_every_commit', type=int, action='store')
    repo_path = parser.parse_args().repo_path
    test_every_commit = parser.parse_args().test_every_commit

    # Settings
    dispatcher_host = 'localhost'
    dispatcher_port = 8888

    repo_clone_pusher = repo_path + '/repo_clone_pusher'
    # Waiting time to check repo in seconds
    schedule = 10


    # Start
    if test_every_commit:
        main_job(repo_clone_pusher, dispatcher_host, dispatcher_port)
    else:
        observe(repo_clone_pusher, dispatcher_host, dispatcher_port, schedule)