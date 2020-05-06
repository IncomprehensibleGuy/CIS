def kill_process(id: int):
    from os import kill
    from signal import SIGTERM
    try:
        kill(id, SIGTERM)
        return 0
    except:
        return -1


if __name__ == '__main__':
    pass