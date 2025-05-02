from abc import ABC, abstractmethod

class BaseTool(ABC):
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
    @abstractmethod
    def run(self, **kwargs) -> str:
        pass
