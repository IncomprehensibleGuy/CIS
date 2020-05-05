import socket
import helpers


def push_commit_to_dispatcher():
    # Settings
    dispatcher_host = 'localhost'
    dispatcher_port = 8888
    commit_id_path = 'C:/Users/Greg/Desktop/Projects/CIS/commit_id.txt'

    try:
        # Call the bash script that will update the repo and check for changes.
        # If there's a change, it will drop a .commit_id file with the latest commit in the current working directory
        subprocess.check_output(['update_repo.sh', repo_clone_obs], shell=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f'Could not update and check repository. Reason: {e.output}')

    if os.path.isfile('.commit_id'):
        # We have a change -> execute the tests

        # Check the status of the dispatcher server to see if we can send the tests
        try:
            response = helpers.communicate(dispatcher_host, int(dispatcher_port), 'status')
        except error:
            raise Exception(f'Could not communicate with dispatcher server: {error}')

        if response == 'OK':
            # Dispatcher is working -> send it commit
            commit_file = open('.commit_id', 'r')
            commit = commit_file.readline()
            commit_file.close()
            response = helpers.communicate(dispatcher_host, int(dispatcher_port), 'dispatch:' + commit)
            if response != 'OK':
                raise Exception(f'Could not dispatch the test: {response}')
            print('dispatched!')
        else:
            # Dispatcher is not working
            raise Exception(f'Could not dispatch the test: {response}')


if __name__ == "__main__":
    push_commit_to_dispatcher()