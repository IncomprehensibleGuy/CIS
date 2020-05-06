from socket import socket, AF_INET, SOCK_STREAM


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


def write_process_id(module:str, identifier='', mode='w'):
    # To close module by pid
    pid = os.getpid()
    ids = open('ids.txt', mode)
    ids.write(module + identifier + ':' + str(pid) + '\n')
    ids.close()