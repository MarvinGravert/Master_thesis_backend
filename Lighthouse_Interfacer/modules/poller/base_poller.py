from typing import List
from abc import ABC, abstractmethod

from backend_api.vr_objects import VRObject


class BasePoller(ABC):

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def poll(self) -> List[VRObject]:
        raise NotImplementedError
