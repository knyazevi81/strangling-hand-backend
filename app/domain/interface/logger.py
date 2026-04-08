from abc import abstractmethod, ABC

class LoggerPort(ABC):

    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        ...

    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        ...

    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        ...