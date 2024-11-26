import threading
import time
import sys

class Counter:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()

class IncrementThread(threading.Thread):
    def __init__(self, counter, iterations, thread_id):
        threading.Thread.__init__(self)
        self.counter = counter
        self.iterations = iterations
        self.thread_id = thread_id
        
    def run(self):
        print(f"Инкрементирующий поток {self.thread_id} начал работу", flush=True)
        for i in range(self.iterations):
            with self.counter.lock:
                local_var = self.counter.value
                local_var += 1
                time.sleep(0.0001)
                self.counter.value = local_var
            if i % 10000 == 0:
                print(f"Инкрементирующий поток {self.thread_id}: {i} операций", flush=True)

class DecrementThread(threading.Thread):
    def __init__(self, counter, iterations, thread_id):
        threading.Thread.__init__(self)
        self.counter = counter
        self.iterations = iterations
        self.thread_id = thread_id
        
    def run(self):
        print(f"Декрементирующий поток {self.thread_id} начал работу", flush=True)
        for i in range(self.iterations):
            with self.counter.lock:
                local_var = self.counter.value
                local_var -= 1
                time.sleep(0.0001)
                self.counter.value = local_var
            if i % 10000 == 0:
                print(f"Декрементирующий поток {self.thread_id}: {i} операций", flush=True)

def main():
    # Уменьшаем количество итераций для теста
    n = 10000
    m = 10000
    
    print("=== Программа запущена ===", flush=True)
    
    start_time = time.time()
    counter = Counter()
    
    # Создаем и запускаем потоки
    inc_thread = IncrementThread(counter, n, 1)
    dec_thread = DecrementThread(counter, m, 1)
    
    print("Запуск потоков...", flush=True)
    
    inc_thread.start()
    dec_thread.start()
    
    print("Ожидание завершения потоков...", flush=True)
    
    inc_thread.join()
    dec_thread.join()
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Выводим результаты
    print("\nРезультаты:", flush=True)
    print(f"Начальное значение счетчика: 0", flush=True)
    print(f"Количество инкрементирующих операций: {n}", flush=True)
    print(f"Количество декрементирующих операций: {m}", flush=True)
    print(f"Конечное значение счетчика: {counter.value}", flush=True)
    print(f"Время выполнения: {execution_time:.4f} секунд", flush=True)
    print("=== Программа завершена ===", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Произошла ошибка: {e}", flush=True)
        sys.exit(1)
