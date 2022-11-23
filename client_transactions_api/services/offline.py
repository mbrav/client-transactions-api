import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class OfflineException(Exception):
    """Custom Offline Exception"""

    def __init__(self, message='Service entering into an offline state'):
        self.message = message
        logger.warning(message)
        super().__init__(self.message)

    def __str__(self):
        return self.message


@dataclass
class OfflineTransaction:
    sum: float


class OfflineTransactions:
    """Offline Database Singleton class"""

    __instance = None
    tokens: dict[str, str] = {}
    transactions: dict[str, OfflineTransaction] = {}

    def __init__(self):
        raise RuntimeError('Call OfflineTransactions.instance() instead')

    @classmethod
    def instance(cls):
        """Return singleton instance"""
        if cls.__instance is None:
            logger.debug('Creating Offline Database Instance')
            cls.__instance = cls.__new__(cls)
        return cls.__instance

    @classmethod
    def add_token(cls, user: str, token: str) -> None:
        """Add a valid user token to dict"""
        self = cls.instance()
        if user not in self.tokens.keys():
            self.tokens[user] = token

    @classmethod
    def check_token(cls, token: str) -> bool:
        """Check if token is valid"""
        self = cls.instance()
        if token not in self.tokens.values():
            return False
        return True
