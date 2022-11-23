import asyncio
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class OfflineException(Exception):
    """Custom Offline Exception"""

    def __init__(self, message='Service entering into an offline state'):
        self.message = message
        logger.warning(message)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InsufficientFundsException(Exception):
    """Offline Exception for insufficient funds"""

    def __init__(self, balance: float, sum: float):
        self.balance = balance
        self.sum = sum
        self.message = f'Not enough funds ({balance:.2f}) for a {sum:.2f} transaction!'
        logger.warning(self.message)
        super().__init__(self.message)

    def __str__(self):
        return self.message


class OfflineUserUnavailable(Exception):
    """Offline Exception for insufficient funds"""


@dataclass
class OfflineTransaction:
    sum: float


@dataclass
class UserData:
    token: str = field(default_factory=str)
    balance: float = field(default_factory=float)


class OfflineTransactions:
    """Offline Database Singleton class"""

    __instance = None
    user_ids: dict[str, int] = {}
    user_names: dict[int, str] = {}
    user_data: dict[str, UserData] = {}
    users_offline: list[str] = []

    def __init__(self):
        raise RuntimeError('Call OfflineTransactions.instance() instead')

    def __len__(self):
        """Return length of users that need to be processed once db is online"""
        return len(self.users_offline)

    @classmethod
    def instance(cls):
        """Return singleton instance"""
        if cls.__instance is None:
            logger.debug('Creating Offline Database Instance')
            cls.__instance = cls.__new__(cls)
        return cls.__instance

    @classmethod
    def add_auth_data(cls, user_id: int, username: str, token: str) -> None:
        """Add valid auth user data to dict"""
        self = cls.instance()
        if username not in self.user_data.keys():
            self.user_data[username] = UserData(token=token)
            logger.info(f'Added user {username} (#{user_id}) to offline database storage')
        else:
            self.user_data[username].token = token
        self.user_ids[username] = user_id
        self.user_names[user_id] = username

    @classmethod
    def add_balance(cls, user_id: int, balance: float) -> None:
        """Add user's balance"""
        self = cls.instance()
        if user_id not in self.user_ids.values():
            logger.warning(
                f'User #{user_id} not available for offline transaction '
                'processing because they have not authenticated yet during '
                'applications runtime')
            return
        username = self.user_names[user_id]
        if username not in self.user_data.keys():
            self.user_data[username] = UserData(balance=balance)
        else:
            self.user_data[username].balance = balance

    @classmethod
    def get_balance(cls, username: str) -> float | OfflineUserUnavailable:
        """Get user's balance value"""
        self = cls.instance()
        user = self.user_data.get(username) or None
        if user is None:
            return OfflineUserUnavailable()
        return user.balance

    @classmethod
    def _check_transaction(cls, balance: float, sum: float) -> bool:
        if balance + sum < 0:
            return False
        return True

    @classmethod
    def transaction(
        cls,
        user_id: int,
        sum: float
    ) -> float | OfflineUserUnavailable | InsufficientFundsException:
        """Add transaction to user's balance"""
        self = cls.instance()
        if user_id not in self.user_ids.values():
            return OfflineUserUnavailable()
        else:
            username = self.user_names[user_id]
            if username not in self.user_data.keys():
                return OfflineUserUnavailable()
            balance = self.user_data[username].balance
            valid = self._check_transaction(balance, sum)
            if not valid:
                return InsufficientFundsException(balance, sum)
            self.user_data[username].balance = balance + sum
            if username not in self.users_offline:
                self.users_offline.append(username)
            return self.user_data[username].balance


class OfflineTransactionPool:
    """Offline Transaction Pool class

    Checks for available tasks to process once DB comes back online
    """

    def __init__(self, interval: int = 5):
        """Set pool interval in seconds"""
        self.interval = interval

    async def run(self):
        """Run executor and check for tasks with interval"""
        while True:
            await asyncio.sleep(self.interval)
            offline_transactions = OfflineTransactions.instance()

            if len(offline_transactions) > 0:
                logger.warning(
                    f'There are {len(offline_transactions)} offline transactions to be processed')
            else:
                logger.debug('No offline transactions at this time')
