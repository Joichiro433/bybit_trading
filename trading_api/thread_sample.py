import time

from concurrent.futures import ThreadPoolExecutor

pooling = []

def wait_pool():
    i = 1
    while True:
        pooling.append(i)
        time.sleep(3)
        i += 1

def print_pooling():
    while True:
        print(pooling)
        time.sleep(2)

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="thread") as executor:
            executor.submit(wait_pool)
            executor.submit(print_pooling)


