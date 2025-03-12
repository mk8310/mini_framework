from typing import Type

import fire

from .command_base import Command


class CLI:
    class CommandLineInterface:
        def __init__(self):
            """
            CLI application for managing various services.
            """
            self.__commands = {}

        def _register(self, name, module_type: Type[Command], **kwargs):
            """
            Registers a module with the CLI.
            Args:
              name: The name of the module.
              module_type: The type of the module.
            """
            self.__commands[name] = module_type(**kwargs).run

        @property
        def _commands(self):
            return self.__commands

    def __init__(self, root_path):
        """
        CLI application for managing various services.
        """
        from mini_framework.context import env
        env.app_root = root_path
        self.__cli = self.CommandLineInterface()

    def register(self, name, module_type: Type[Command], **kwargs):
        """
        Registers a module with the CLI.
        Args:
          name: The name of the module.
          module_type: The type of the module.
        """
        self.__cli._register(name, module_type, **kwargs)

    @property
    def cli(self) -> CommandLineInterface:
        return self.__cli

    def setup(self):
        """
        Sets up the CLI application.
        """
        for name, module in self.__cli._commands.items():
            setattr(self.__cli, name, module)

        fire.Fire(self.__cli)
