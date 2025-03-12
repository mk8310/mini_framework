import threading

from .process import Process


class ProcessManager:
    def __init__(self, max_processes):
        """
        进程管理器
        :param max_processes: 最大进程数
        """
        self.__processes: dict[int, Process] = {}  # pid -> Process
        self.__lock = threading.Lock()
        self.__max_processes = max_processes
        self.__semaphore = threading.Semaphore(max_processes)

    def start_process(self, proc: Process):
        """
        添加进程
        :param proc: 进程
        :return:
        """
        self.__semaphore.acquire()

        with self.__lock:
            proc.start(self.__semaphore)
            self.__processes[proc.pid] = proc
        return proc  # Return the Process instance

    def terminate_process(self, pid):
        with self.__lock:
            if pid in self.__processes:
                self.__processes[pid].terminate()
                del self.__processes[pid]

    def get_process(self, pid):
        with self.__lock:
            return self.__processes.get(pid)

    def cleanup_finished_processes(self):
        with self.__lock:
            finished_pids = [
                pid for pid, proc in self.__processes.items() if proc.is_finished()
            ]
            for pid in finished_pids:
                self.__processes[pid].stdout_thread.join()
                self.__processes[pid].stderr_thread.join()
                del self.__processes[pid]
                self.__semaphore.release()
