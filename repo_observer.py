import os
import socket
import subprocess
import time

import helpers


def poll():
    # settings
    dispatcher_host = 'localhost'
    dispatcher_port = 8888
    observing_repo = 'C:/Users/Greg/Desktop/Projects/CIS/monitoring_repo/repo_clone_obs'  # Paste path to the repo on your machine

    while True:
        try:
            # call the bash script that will update the repo and check
            # for changes. If there's a change, it will drop a .commit_id file
            # with the latest commit in the current working directory
            subprocess.check_output(["update_repo.sh", observing_repo], shell=True)
        except subprocess.CalledProcessError as e:
            raise Exception("Could not update and check repository. Reason: %s" % e.output)

        if os.path.isfile(".commit_id"):
            # great, we have a change! let's execute the tests
            # First, check the status of the dispatcher server to see
            # if we can send the tests
            try:
                response = helpers.communicate(dispatcher_host, int(dispatcher_port), b"status")
                response =  response.decode('utf-8')
            except socket.error as e:
                raise Exception("Could not communicate with dispatcher server: %s" % e)

            if response == "OK":
                # Dispatcher is present, let's send it a test
                commit = ""
                with open(".commit_id", "r") as f:
                    commit = f.readline()
                response = helpers.communicate(dispatcher_host, int(dispatcher_port), b"dispatch:%s" % commit)
                response = response.decode('utf-8')

                if response != "OK":
                    raise Exception("Could not dispatch the test: %s" %
                    response)
                print("dispatched!")
            else:
                # Something wrong happened to the dispatcher
                raise Exception("Could not dispatch the test: %s" %
                response)
        time.sleep(5)


if __name__ == "__main__":
    poll()