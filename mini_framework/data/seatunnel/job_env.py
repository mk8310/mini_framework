from enum import Enum

from .config import Config


class JobMode(str, Enum):
    batch = "batch"
    stream = "stream"

    @staticmethod
    def to_list():
        return list(map(lambda c: c.value, JobMode))


class JobEnvironment(Config):

    def validate(self):
        if self.name is None or self.name == "":
            raise ValueError("name 不能为空")
        if self.mode not in JobMode or self.mode is None:
            raise ValueError(f"mode 只能是 {JobMode.batch} 或 {JobMode.stream}")

    def __init__(
        self,
        name,
        mode=JobMode.batch,
        parallelism: int = None,
        execution_parallelism: int = None,
        retry_times: int = None,
        retry_interval_seconds: int = None,
    ):
        """
        初始化 Seatunnel 作业环境配置
        :param name: 作业名称
        :param mode: 作业模式
        :param parallelism: 作业并行度，仅在 mode 为 stream 时有效
        :param retry_times:
        :param retry_interval_seconds:
        """
        self.mode = mode
        self.name = name.strip() if name else name
        self.parallelism = parallelism
        self.execution_parallelism = execution_parallelism
        self.retry_times = retry_times
        self.retry_interval_seconds = retry_interval_seconds

    def _to_dict(self):
        result = {
            "job.mode": self.mode,
            "job.name": self.name,
            "parallelism": self.parallelism,
            "execution.parallelism": self.execution_parallelism,
            "job.retry.times": self.retry_times,
            "job.retry.interval.seconds": self.retry_interval_seconds,
        }

        if self.parallelism is None:
            result.pop("parallelism")
        if self.execution_parallelism is None:
            result.pop("execution.parallelism")
        if self.retry_times is None:
            result.pop("job.retry.times")
        if self.retry_interval_seconds is None:
            result.pop("job.retry.interval.seconds")

        return result
