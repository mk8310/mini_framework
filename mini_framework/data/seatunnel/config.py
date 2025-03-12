from abc import ABC, abstractmethod


class Config(ABC):
    """Seatunnel 基础配置类"""

    def to_dict(self):
        self.validate()
        return self._to_dict()

    @abstractmethod
    def _to_dict(self) -> dict:
        pass

    @abstractmethod
    def validate(self):
        pass
