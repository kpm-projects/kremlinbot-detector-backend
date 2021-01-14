import threading

from data_collection.bots import main as bots_main
from data_collection.politicians import main as politicians_main

if __name__ == '__main__':
    threading.Thread(target=bots_main).start()
    politicians_main()
