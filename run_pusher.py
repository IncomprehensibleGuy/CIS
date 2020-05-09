if __name__ == '__main__':
    import os
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('pusher_path', type=str, action='store')
    parser.add_argument('repo_path', type=str, action='store')

    args = parser.parse_args()

    os.system('cd ' + args.pusher_path + ' && py pusher.py ' + args.repo_path +' 1')
    print('pusher is started, run_pusher is done')