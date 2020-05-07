import argparse
import errno
import os
import re
import socket
import socketserver
import subprocess
import time
import threading
import unittest

import helpers


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    repo_folder = None
    dispatcher_host = None # Holds the dispatcher server host/port information
    dispatcher_port = None
    last_communication = None # Keeps track of last communication from dispatcher
    busy = False # Status flag
    is_serving = True # Status flag


class TestHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.
    """

    # ()	Group expression and return detected text
    # \w	Any digit or letter (\W — any except letter or digit)
    # +	    1 or more occurrences of the pattern on the left
    # .	    Any single character except new line \n
    # *	    0 or more occurrences of the pattern on the left
    command_re = re.compile(r"(\w+)(:.+)*")

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).decode('utf-8').strip()
        #print('data accepted:_____________\n', self.data,'\n_____________')
        command_groups = self.command_re.match(self.data)
        command = command_groups.group(1)

        #command = self.data

        if not command:
            self.request.sendall(b'Invalid command')
            return

        if command == 'are_you_working':
            print('pinged')
            self.server.last_communication = time.time()
            self.request.sendall(b'yes')
        elif command == 'runtest':
            print(f'got runtest command: am I busy? {self.server.busy}')
            if self.server.busy:
                self.request.sendall(b'BUSY')
            else:
                self.request.sendall(b'OK')
                print('running')
                commit_id = command_groups.group(2)[1:]
                self.server.busy = True
                self.run_tests(commit_id, self.server.repo_folder)
                self.server.busy = False
        else:
            self.request.sendall(b'Invalid command')

    def run_tests(self, commit_id, repo_folder):
        # Update repo
        subprocess.check_output(['test_runner_script.sh', repo_folder, commit_id], shell=True)
        # Run the tests
        test_folder = os.path.join(repo_folder, 'tests') # repo_folder + tests
        suite = unittest.TestLoader().discover(test_folder)

        result_file = open('results.txt', 'a')
        t = time.strftime('%H:%M:%S  %d.%m.%Y')
        text = '='*70 + f'Test started ad {t}'
        result_file.write(text)
        unittest.TextTestRunner(result_file).run(suite)
        result_file.write('='*70)
        result_file.close()

        result_file = open('results.txt', 'r')
        # Give the dispatcher the results
        output = result_file.read()

        helpers.communicate(self.server.dispatcher_host, self.server.dispatcher_port,
                            f'results:{commit_id}:{len(output)}:{output}')
        result_file.close()
        os.remove('results.txt')


def serve():
    range_start = 8900

    parser = argparse.ArgumentParser()
    parser.add_argument('--host',
                        help='runner\'s host, by default it uses localhost',
                        default='localhost',
                        action='store')
    parser.add_argument('--port',
                        help=f'runner\'s port, by default it uses values >={range_start}',
                        action='store')
    parser.add_argument('--dispatcher-server',
                        help='dispatcher host:port, by default it uses localhost:8888',
                        default='localhost:8888',
                        action='store')
    parser.add_argument('repo',
                        metavar='REPO',
                        type=str,
                        help='path to the repository this will observe')
    args = parser.parse_args()

    # Get servers parameters from command line parser
    test_runner_host = args.host
    test_runner_port = args.port
    dispatcher_host = args.dispatcher_server.split(":")[0]
    dispatcher_port = int(args.dispatcher_server.split(":")[1])
    print(f'Got dispatcher server info - {dispatcher_host}:{dispatcher_port}')

    # Create instance of the test_runner server
    tries = 0
    if not test_runner_port:
        test_runner_port = range_start
        while tries < 100:
            try:
                test_runner_server = ThreadingTCPServer((test_runner_host, test_runner_port), TestHandler)
                break
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    tries += 1
                    test_runner_port += tries
                    continue
                else:
                    raise e
        else:
            raise Exception(f'Could not bind to ports in range {range_start}-{range_start + tries}')
    else:
        test_runner_server = ThreadingTCPServer((test_runner_host, test_runner_port), TestHandler)

    test_runner_server.repo_folder = args.repo
    test_runner_server.dispatcher_host = dispatcher_host
    test_runner_server.dispatcher_port = dispatcher_port
    print(f'Test runner serving on {test_runner_host}:{test_runner_port}')

    # To identify specific test runner (may be several) add port to module name and send it pid
    helpers.write_process_id('test_runner', identifier=str(test_runner_port), mode='a')

    # Try to register test runner with dispatcher
    response = helpers.communicate(dispatcher_host, dispatcher_port, f'register:{test_runner_host}:{test_runner_port}')
    if response != 'OK':
        raise Exception('Can\'t register with dispatcher!')

    def dispatcher_checker(test_runner_server):
        # Checks if the dispatcher went down.
        # If it is down, we will shut down if since the dispatcher may not have the same host/port when it comes back up.
        while test_runner_server.is_serving:
            time.sleep(5)
            if (time.time() - test_runner_server.last_communication) > 10:
                try:
                    response = helpers.communicate(test_runner_server.dispatcher_host,
                                                   test_runner_server.dispatcher_port,
                                                   'status')
                    if response != 'OK':
                        print('Dispatcher is no longer functional')
                        test_runner_server.shutdown()
                        return
                except socket.error as e:
                    print(f'Can\'t communicate with dispatcher: {e}')
                    test_runner_server.shutdown()
                    return

    t = threading.Thread(target=dispatcher_checker, args=(test_runner_server,))
    try:
        t.start()
        # Activate the server; this will keep running until interrupt ( Ctrl-C )
        test_runner_server.serve_forever()
    except (KeyboardInterrupt, Exception):
        # If any exception occurs, kill the thread
        test_runner_server.is_serving = False
        t.join()


if __name__ == '__main__':
    serve()