import threading
import time

from data_collection.bots import main as bots_main
from data_collection.politicians import main as politicians_main

if __name__ == '__main__':
    start_time = time.time()

    bots_thread = threading.Thread(target=bots_main)
    politicians_thread = threading.Thread(target=politicians_main)

    bots_thread.start()
    politicians_thread.start()

    bots_thread.join()
    politicians_thread.join()

    print("--- %s seconds ---" % (time.time() - start_time))
