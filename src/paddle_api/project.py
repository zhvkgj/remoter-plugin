#!/usr/bin/env python3
from abc import ABC, abstractmethod

from config import PaddleProjectConfig
from config_spec import PaddleProjectConfigSpec
from plugin import MessageType


class PaddleProject(ABC):
    """
    Abstract class represents Paddle Project API with async methods.
    """

    @abstractmethod
    async def print_message(self, message: str, message_type: MessageType):
        pass

    @property
    @abstractmethod
    def working_dir(self) -> str:
        pass

    @property
    @abstractmethod
    def config(self) -> PaddleProjectConfig:
        pass


class ExtendedPaddleProject(PaddleProject):
    """
    Abstract class extends Paddle Project API with methods to extend project's configuration specification.
    """

    @property
    @abstractmethod
    def config_spec(self) -> PaddleProjectConfigSpec:
        pass
