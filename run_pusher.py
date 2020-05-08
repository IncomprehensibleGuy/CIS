if __name__ == '__main__':
    import os
    import argparse
    #os.system('start cmd /K "cd C:/Users/Greg/Desktop/Projects/CIS/source/ && py pusher.py 1"')

    parser = argparse.ArgumentParser()
    parser.add_argument('repo_path', type=str, action='store')


    os.system('cd C:/Users/Greg/Desktop/Projects/CIS/source/ && py pusher.py ' + parser.parse_args().repo_path +' 1')
    print('pusher is started, run_pusher is done')