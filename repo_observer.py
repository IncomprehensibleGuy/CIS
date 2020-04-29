import os
import socket
import subprocess
import time

import helpers


def push_commit_to_tests():
    # Settings
    dispatcher_host = 'localhost'
    dispatcher_port = 8888
    observing_repo_clone = 'C:/Users/Greg/Desktop/Projects/CIS/monitoring_repo/repo_clone_obs'

    # Call the bash script that will update the repo and check for changes.
    # If there's a change, it will drop a .commit_id file with the latest commit in the current working dir.
    try:
        subprocess.check_output(['update_repo.sh', observing_repo_clone], shell=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f'Could not update and check repository. Reason: {e.output}')

    if os.path.isfile('.commit_id'):
        # We have a change -> execute the tests
        # First, check the status of the dispatcher server to see if we can send the tests
        try:
            response = helpers.communicate(dispatcher_host, dispatcher_port, b'status')
            response =  response.decode('utf-8')
        except socket.error as e:
            raise Exception(f'Could not communicate with dispatcher server: {e}')

        if response == 'OK':
            # Dispatcher is present -> send it a test
            commit = ''
            with open('.commit_id', 'r') as f:
                commit = f.readline()
            response = helpers.communicate(dispatcher_host, dispatcher_port, ('dispatch:' + commit).encode())
            response = response.decode('utf-8')
            if response != 'OK': raise Exception(f'Could not dispatch commit: {response}')
            print("commit dispatched")
        else:
            # Something wrong happened to the dispatcher
            raise Exception(f"Could not dispatch the test: {response}")


if __name__ == "__main__":
    push_commit_to_tests()