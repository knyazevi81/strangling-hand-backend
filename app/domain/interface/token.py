class AbstractTokenService(ABC):
    @abstractmethod
    def create_pair(self, user_id: str) -> TokenPair:
        ...

    @abstractmethod
    def decode_access(self, token: str) -> TokenPayload:
        ...

    @abstractmethod
    def decode_refresh(self, token: str) -> TokenPayload:
        ...