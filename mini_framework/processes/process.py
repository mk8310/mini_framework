import queue
import subprocess
import threading


def _enqueue_output(out, process_queue):
    for line in iter(out.readline, ""):
        process_queue.put(line)
    out.close()


class Process:
    def __init__(self, cmd, *args, **kwargs):
        """
        初始化进程上下文管理器
        :param cmd: 需要执行的命令
        """
        self.__started = False
        self.__pid: int = -1
        self.__stdout_queue: queue.Queue = None
        self.__stderr_queue: queue.Queue = None
        self.__stderr_thread: threading.Thread = None
        self.__stdout_thread: threading.Thread = None
        self.__process: subprocess.Popen = None
        self.__cmd = cmd
        self.__args = args
        self.__kwargs = kwargs
        self.__semaphore = None

    def start(self, semaphore):
        """
        启动进程
        :param semaphore: 信号量，用于控制最大进程数
        :return:
        """
        self.__semaphore = semaphore
        self.__stdout_queue: queue.Queue = queue.Queue()
        self.__stderr_queue: queue.Queue = queue.Queue()
        args = [self.__cmd] + list(self.__args)
        self.__process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            **self.__kwargs
        )

        self.__stdout_thread = threading.Thread(
            target=_enqueue_output, args=(self.__process.stdout, self.__stdout_queue)
        )
        self.__stderr_thread = threading.Thread(
            target=_enqueue_output, args=(self.__process.stderr, self.__stderr_queue)
        )
        self.__stdout_thread.daemon = True
        self.__stderr_thread.daemon = True
        self.__stdout_thread.start()
        self.__stderr_thread.start()
        self.__pid = self.__process.pid
        self.__started = True

    def __check_started(self):
        if not self.__started:
            raise ValueError("Process not started")

    @property
    def stdout_thread(self):
        """
        获取标准输出线程
        :return: 标准输出线程
        """
        self.__check_started()
        return self.__stdout_thread

    @property
    def stderr_thread(self):
        """
        获取标准错误输出线程
        :return: 标准错误输出线程
        """
        self.__check_started()
        return self.__stderr_thread

    @property
    def pid(self):
        """
        获取进程 ID
        :return: 进程 ID
        """
        self.__check_started()
        return self.__pid

    def get_stdout(self):
        """
        获取标准输出
        :return: 标准输出（多行）
        """
        self.__check_started()
        lines = []
        while True:
            try:
                line = self.__stdout_queue.get_nowait()
            except queue.Empty:
                break
            else:
                lines.append(line)
        return lines

    def get_stderr(self):
        """
        获取标准错误输出
        :return: 标准错误输出（多行）
        """
        self.__check_started()
        lines = []
        while True:
            try:
                line = self.__stderr_queue.get_nowait()
            except queue.Empty:
                break
            else:
                lines.append(line)
        return lines

    def terminate(self):
        """
        终止进程
        :return:
        """
        self.__check_started()

        if self.__process.poll() is None:
            self.__process.terminate()
            self.__process.wait()
        self.__stdout_thread.join()
        self.__stderr_thread.join()
        self.__semaphore.release()

    def is_finished(self):
        """
        判断进程是否结束, 如果进程未启动，则返回 True
        :return: 进程是否结束
        """
        if self.__process is None:
            return True
        return self.__process.poll() is not None
