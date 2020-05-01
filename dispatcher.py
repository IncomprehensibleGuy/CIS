import os
import re
import socket
import socketserver
import time
import threading

import helpers


# Shared dispatcher code
def dispatch_tests(server, commit_id):
    # NOTE: usually we don't run this forever
    while True:
        print('trying to dispatch to runners')
        for runner in server.runners:
            response = helpers.communicate(runner['host'], int(runner['port']), 'runtest:'+commit_id)

            if response == 'OK':
                print(f'adding id {commit_id}')
                server.dispatched_commits[commit_id] = runner
                if commit_id in server.pending_commits:
                    server.pending_commits.remove(commit_id)
                return

        time.sleep(2)


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    runners = [] # Keeps track of test runner pool
    is_serving = True # Indicate to other threads that we are no longer running
    dispatched_commits = {} # Keeps track of commits we dispatched
    pending_commits = [] # Keeps track of commits we have yet to dispatch


class DispatcherHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our dispatcher.
    This will dispatch test runners against the incoming commit and handle their requests and test results
    """

    # ()	Группирует выражение и возвращает найденный текст
    # \w	Любая цифра или буква (\W — все, кроме буквы или цифры)
    # +	    1 и более вхождений шаблона слева
    # .	    Один любой символ, кроме новой строки \n
    # *	    0 и более вхождений шаблона слева
    command_re = re.compile(r"(\w+)(:.+)*")
    BUF_SIZE = 1024

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(self.BUF_SIZE).decode('utf-8').strip()
        command_groups = self.command_re.match(self.data)

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
            runner = {'host': host, 'port':port}
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

    # Create a thread to check the runner pool
    def runner_checker(server):
        def manage_commit_lists(runner):
            for commit, assigned_runner in server.dispatched_commits.iteritems():
                if assigned_runner == runner:
                    del server.dispatched_commits[commit]
                    server.pending_commits.append(commit)
                    break
            server.runners.remove(runner)

        while server.is_serving:
            time.sleep(1)
            for runner in server.runners:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    response = helpers.communicate(runner['host'], int(runner['port']), 'ping')
                    if response != 'pong':
                        print(f'removing runner {runner}')
                        manage_commit_lists(runner)
                except socket.error as e:
                    manage_commit_lists(runner)

    # This will kick off tests that failed
    def redistribute(server):
        while server.is_serving:
            for commit in server.pending_commits:
                print("running redistribute")
                print(server.pending_commits)
                dispatch_tests(server, commit)
                time.sleep(5)

    runner_heartbeat = threading.Thread(target=runner_checker, args=(dispatcher_server,))
    redistributor = threading.Thread(target=redistribute, args=(dispatcher_server,))
    try:
        runner_heartbeat.start()
        redistributor.start()
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl+C or Cmd+C
        dispatcher_server.serve_forever()
    except (KeyboardInterrupt, Exception):
        # If any exception occurs, kill the thread
        dispatcher_server.is_serving = False
        runner_heartbeat.join()
        redistributor.join()


if __name__ == "__main__":
    serve()