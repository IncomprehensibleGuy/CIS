import socket


def communicate(host, port, message) -> str:
    ''' Helper-method to communicate repo_observer, dispatcher and test_runner
        :returns bytes object response
    '''

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(bytes(message, encoding='utf-8'))
    response = s.recv(1024).decode('utf-8')
    s.close()

    return response