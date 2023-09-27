import multiprocessing

def run_server():
  from servers.control_server import serve
  serve()

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    p = multiprocessing.Process(target=run_server)
    p.start()
    p.join()