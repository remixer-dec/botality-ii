import multiprocessing
import os
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--env', type=str, help='Path to environment configuration file', default='.env')

def run_server():
  from servers.control_server import serve
  serve()

if __name__ == "__main__":
    args = parser.parse_args()
    os.environ['BOTALITY_ENV_FILE'] = args.env
    multiprocessing.set_start_method('spawn')
    p = multiprocessing.Process(target=run_server)
    p.start()
    p.join()