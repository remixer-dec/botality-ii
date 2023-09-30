import multiprocessing
import os
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--env', type=str, help='Path to environment configuration file', default='.env')
parser.add_argument('--autostart', action='store_true', help='Start the bot with the webui', default=False)

def run_server():
  from servers.control_server import serve
  serve()

if __name__ == "__main__":
    args = parser.parse_args()
    os.environ['BOTALITY_ENV_FILE'] = args.env
    os.environ['BOTALITY_AUTOSTART'] = str(args.autostart)
    multiprocessing.set_start_method('spawn')
    p = multiprocessing.Process(target=run_server)
    p.start()
    p.join()