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