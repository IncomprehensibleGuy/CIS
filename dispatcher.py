import os
import re
import socketserver
import threading
from socket import error
from time import sleep

import helpers


def dispatch_tests(dispatcher_server, commit_id):
    ''' Push commit to free test runner'''

    # This function should not run forever, because we should have enough free test runners
    while True:
        print('trying to push commit to free test runner')
        for runner in dispatcher_server.runners:
            response = helpers.communicate(runner['host'], runner['port'], 'runtest:'+commit_id)

            if response == 'OK':
                # Free test runner found ->
                # 1) add manage commit and its runner to dispatched commits dictionary
                # 2) remove commit from pending commits list
                print(f'adding commit id {commit_id}')
                dispatcher_server.dispatched_commits[commit_id] = runner
                if commit_id in dispatcher_server.pending_commits:
                    dispatcher_server.pending_commits.remove(commit_id)
                return
        print('no free test runners')
        sleep(2)


def runners_checker(dispatcher_server):
    ''' Thread function to check the runner pool '''

    def remove_runner(runner):
        ''' Manage commit list with commit belongs runner and remove runner from dispatcher server runner's list'''
        for commit, assigned_runner in dispatcher_server.dispatched_commits.items():
            if assigned_runner == runner:
                del dispatcher_server.dispatched_commits[commit]
                dispatcher_server.pending_commits.append(commit)
                break
        dispatcher_server.runners.remove(runner)

    while dispatcher_server.is_serving:
        sleep(1)
        for runner in dispatcher_server.runners:
            try:
                response = helpers.communicate(runner['host'], runner['port'], 'are_you_working')
                if response != 'yes':
                    print(f'removing runner {runner}')
                    remove_runner(runner)
            except error:
                remove_runner(runner)


def redistribute(dispatcher_server):
    ''' Thread function redistribute free test runners between every pending commit '''

    while dispatcher_server.is_serving:
        for commit in dispatcher_server.pending_commits:
            print(f'running redistribute with commits:\n{dispatcher_server.pending_commits}')
            dispatch_tests(dispatcher_server, commit)
            sleep(5)


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    is_serving = True  # Indicate to other threads that we are no longer running
    runners = [] # Keeps track of test runner pool
    pending_commits = []  # Keeps track of commits we have yet to dispatch
    dispatched_commits = {} # Keeps track of commits we dispatched


class DispatcherHandler(socketserver.BaseRequestHandler):
    '''
    The RequestHandler class for our dispatcher.
    This will dispatch test runners against the incoming commit and handle their requests and test results.
    '''

    # ()	Group expression and return detected text
    # \w	Any digit or letter (\W — any except letter or digit)
    # +	    1 or more occurrences of the pattern on the left
    # .	    Any single character except new line \n
    # *	    0 or more occurrences of the pattern on the left
    command_pattern = re.compile(r"(\w+)(:.+)*")
    BUF_SIZE = 1024

    def handle(self):
        ''' ?  '''
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(self.BUF_SIZE).decode('utf-8').strip()
        command_groups = self.command_pattern.match(self.data)

        if not command_groups:
            self.request.sendall(b'Invalid command')
            return

        command = command_groups.group(1)

        if command == 'status':
            print('in status')
            self.request.sendall(b'OK')
        elif command == 'register':
            # Add this test runner to our pool
            print('register')
            address = command_groups.group(2)
            host, port = re.findall(r":(\w*)", address)
            runner = {'host': host, 'port': int(port)}
            self.server.runners.append(runner)
            self.request.sendall(b'OK')
        elif command == 'dispatch':
            print('going to dispatch')
            commit_id = command_groups.group(2)[1:]
            if not self.server.runners:
                self.request.sendall(b'No runners are registered')
            else:
                # The coordinator can trust us to dispatch the test
                self.request.sendall(b'OK')
                dispatch_tests(self.server, commit_id)
        elif command == 'results':
            print('got test results')
            results = command_groups.group(2)[1:]
            results = results.split(':')
            commit_id = results[0]
            length_msg = int(results[1])
            # 3 is the number of ":" in the sent command
            remaining_buffer = self.BUF_SIZE - (len(command) + len(commit_id) + len(results[1]) + 3)
            if length_msg > remaining_buffer:
                self.data += self.request.recv(length_msg - remaining_buffer).decode('utf-8').strip()
            del self.server.dispatched_commits[commit_id]

            if not os.path.exists('test_results'):
                os.makedirs('test_results')
            with open(f'test_results/{commit_id}', 'w') as file:
                data = self.data.split(":")[3:]
                data = '\n'.join(data)
                file.write(data)
            self.request.sendall(b'OK')
            print('-----------------------')
        else:
            self.request.sendall(b'Invalid command')


def serve():
    # Settings
    server_host = 'localhost'
    server_port = 8888

    # Create the server
    dispatcher_server = ThreadingTCPServer((server_host, server_port), DispatcherHandler)
    print(f'Dispatcher socket - {server_host}:{server_port}')

    runners_checker_thread = threading.Thread(target=runners_checker, args=(dispatcher_server,))
    redistributor_thread = threading.Thread(target=redistribute, args=(dispatcher_server,))

    try:
        runners_checker_thread.start()
        redistributor_thread.start()
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl+C or Cmd+C
        dispatcher_server.serve_forever()
    except (KeyboardInterrupt, Exception):
        # If any exception occurs, kill the thread
        dispatcher_server.is_serving = False
        runners_checker_thread.join()
        redistributor_thread.join()


if __name__ == "__main__":
    serve()