import threading
import time




def print_time(thread_name, delay):
    count = 0
    number = 1

    while count < 5:
        time.sleep(delay)
        count += 1
        number += 1
        print(thread_name, time.ctime(), number)


thread1 = threading.Thread(
    target=print_time,
    args=("Thread-1", 0.5),
)

thread2 = threading.Thread(
    target=print_time,
    args=("Thread-2", 0.8),
)

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print("程序结束")