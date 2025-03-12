import os.path

from .seatunnel import SeatunnelConfig
from ...context import env
from ...processes.process import Process


def _check_seatunnel_installed(cmd: str) -> str:
    """
    检查 seatunnel 是否安装
    """
    if cmd:
        if not os.path.exists(cmd):
            raise ValueError(f"seatunnel command '{cmd}' not found")
        if not os.access(cmd, os.X_OK):
            raise ValueError(f"seatunnel command '{cmd}' not executable")
        if  os.path.splitext(cmd)[1] != ".sh":
            raise ValueError(f"seatunnel command '{cmd}' not executable")
        return cmd

    for path in os.environ["PATH"].split(os.pathsep):
        path = path.strip('"')
        exe_file = os.path.join(path, "seatunnel.sh")
        if os.path.exists(exe_file) and os.access(exe_file, os.X_OK):
            return exe_file

    for root, dirs, files in os.walk(env.root_path):
        for file in files:
            if file == "seatunnel.sh":
                exec_file = os.path.join(root, file)
                if os.access(exec_file, os.X_OK):
                    return str(exec_file)

    for root, dirs, files in os.walk("/opt"):
        for file in files:
            if file == "seatunnel.sh":
                exec_file = os.path.join(root, file)
                if os.access(exec_file, os.X_OK):
                    return str(exec_file)

    raise ValueError("seatunnel command not found")


class SeatunnelProcess(Process):

    def __init__(self, cmd_path, config: SeatunnelConfig, *args, **kwargs):
        """
        通过 seatunnel 实现数据处理
        :param cmd: seatunnel 命令路径
        :param args:
        :param kwargs:
        """
        cmd_path = _check_seatunnel_installed(cmd_path)
        config.save(env.seatunnel_config_path)
        # args.append("--config")
        seatunnel_args = ["--config", env.seatunnel_config_path]
        super(SeatunnelProcess, self).__init__(
            cmd_path, *args, *seatunnel_args, **kwargs
        )
