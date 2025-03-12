from mini_framework.commands.command_base import Command
from mini_framework.context import env
from mini_framework.utils.modules import import_callable


class WebCommand(Command):
    def __init__(self, router_func_module: str, **kwargs):
        """
        Initializes the web command.
        Args:
          **kwargs: The keyword arguments passed to the command.
        """
        self.__router_func_module = router_func_module
        super().__init__(**kwargs)

    def run(self, host="127.0.0.1", port=8080):
        """
        启动Web服务器。
        :param host: Web服务器运行的主机。
        :param port: Web服务器监听的端口。
        """
        env.sync_type = "async"
        router_func = import_callable(self.__router_func_module)
        router_func()
        from mini_framework.web.app_context import ApplicationContextManager
        application_context_manager = ApplicationContextManager()
        application_context_manager.initialize()
        application_context_manager.run(host, port)
