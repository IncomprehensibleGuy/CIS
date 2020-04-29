import socket

import helpers


def push_commit_to_dispatcher():
    # Settings
    dispatcher_host = 'localhost'
    dispatcher_port = 8888
    commit_id_path = 'C:/Users/Greg/Desktop/Projects/CIS/commit_id.txt'

    # Check the status of the dispatcher server to see if we can send the tests
    try:
        response = helpers.communicate(dispatcher_host, dispatcher_port, b'status')
        response =  response.decode('utf-8')
    except socket.error as e:
        raise Exception(f'Could not communicate with dispatcher server: {e}')

    if response == 'OK':
        # Dispatcher is present -> send it a test
        commit_file = open(commit_id_path, 'r')
        commit = commit_file.readline()
        commit_file.close()
        print(commit)
        response = helpers.communicate(dispatcher_host, dispatcher_port, ('dispatch:' + commit).encode())
        response = response.decode('utf-8')
        if response != 'OK': raise Exception(f'Could not dispatch commit: {response}')
        print("commit dispatched")
    else:
        # Something wrong happened to the dispatcher
        raise Exception(f"Could not dispatch the test: {response}")


if __name__ == "__main__":
    push_commit_to_dispatcher()