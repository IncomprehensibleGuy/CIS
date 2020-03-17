import socket


def communicate(host, port, request):
    ''' Helper-method to communicate repo_observer, dispatcher and test_runner
        :returns bytes object response
    '''

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(request)
    response = s.recv(1024)
    s.close()

    return response