from abc import ABC, abstractmethod

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher


class AbstractPasswordHasher(ABC):
    @abstractmethod
    def hash(self, plain: str) -> str: ...

    @abstractmethod
    def verify(self, plain: str, hashed: str) -> bool: ...


class BcryptPasswordHasher(AbstractPasswordHasher):
    """bcrypt via pwdlib — actively maintained, Python 3.12+ compatible."""

    def __init__(self) -> None:
        self._ph = PasswordHash((BcryptHasher(),))

    def hash(self, plain: str) -> str:
        return self._ph.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        return self._ph.verify(plain, hashed)
