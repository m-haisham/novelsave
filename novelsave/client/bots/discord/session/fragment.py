from abc import ABC, abstractmethod


class SessionFragment(ABC):
    def __init__(self, session):
        self.session = session

    @abstractmethod
    def is_busy(self):
        """Whether the fragment is doing work"""

    def close(self):
        """Close the fragment state"""
        pass
