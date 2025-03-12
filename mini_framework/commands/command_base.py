from abc import ABC, abstractmethod


class Command(ABC):

    def __init__(self, **kwargs):
        """
        Initializes the command.
        Args:
          **kwargs: The keyword arguments passed to the command.
        """
        self.__kwargs = kwargs

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement this method.")
