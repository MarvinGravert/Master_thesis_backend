from typing import List, Tuple
from abc import ABC, abstractmethod

from backend_api.grpc_objects import Tracker, Controller


class BasePoller(ABC):

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def poll(self) -> Tuple[List[Tracker], List[Controller]]:
        raise NotImplementedError
