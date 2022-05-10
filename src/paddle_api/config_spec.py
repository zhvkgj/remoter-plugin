#!/usr/bin/env python3
from abc import ABC, abstractmethod
from typing import List, Dict


class SpecNode(ABC):
    """
    Base class of all configuration specification nodes types.
    """

    @abstractmethod
    def __init__(self, title: str, description: str) -> None:
        self.__title = title
        self.__description = description

    @property
    def title(self) -> str:
        return self.__title

    @title.setter
    def title(self, value: str) -> None:
        self.__title = value

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, value: str) -> None:
        self.__description = value


class CompositeSpecNode(SpecNode):
    def __init__(self, title: str = None, description: str = None, required: List[str] = None,
                 properties: Dict[str, SpecNode] = None, valid_specs: List['CompositeSpecNode'] = None) -> None:
        SpecNode.__init__(self, title=title, description=description)
        self.__required = list() if required is None else required
        self.__properties = dict() if properties is None else properties
        self.__valid_specs = list() if valid_specs is None else valid_specs

    @property
    def required(self) -> List[str]:
        return self.__required

    @property
    def properties(self) -> Dict[str, SpecNode]:
        return self.__properties

    @property
    def valid_specs(self) -> List['CompositeSpecNode']:
        return self.__valid_specs


class ArraySpecNode(SpecNode):
    def __init__(self, title: str = None, description: str = None, items: SpecNode = None) -> None:
        SpecNode.__init__(self, title=title, description=description)
        self.__items = items

    @property
    def items(self) -> SpecNode:
        return self.__items

    @items.setter
    def items(self, value: SpecNode) -> None:
        self.__items = value


class StringSpecNode(SpecNode):
    def __init__(self, title: str = None, description: str = None, valid_values: List[str] = None):
        SpecNode.__init__(self, title=title, description=description)
        self.__valid_values = list() if valid_values is None else valid_values

    @property
    def valid_values(self) -> List[str]:
        return self.__valid_values


class BooleanSpecNode(SpecNode):
    def __init__(self, title: str = None, description: str = None, valid_values: List[bool] = None):
        SpecNode.__init__(self, title=title, description=description)
        self.__valid_values = list() if valid_values is None else valid_values

    @property
    def valid_values(self) -> List[bool]:
        return self.__valid_values


class IntegerSpecNode(SpecNode):
    def __init__(self, title: str = None, description: str = None, valid_values: List[int] = None):
        SpecNode.__init__(self, title=title, description=description)
        self.__valid_values = list() if valid_values is None else valid_values

    @property
    def valid_values(self) -> List[int]:
        return self.__valid_values


class PaddleProjectConfigSpec(ABC):
    """
    Abstract class represents Paddle Project configuration specification.
    Implementation of this class should provide API to change specification
    which used to validate Paddle project's configuration.
    """

    @property
    @abstractmethod
    def root(self) -> CompositeSpecNode:
        """
        Returns the root of the configuration specification tree.
        :return:
        """
        pass

    @abstractmethod
    def contains(self, key: str) -> bool:
        """
        Checks that configuration specification contains the value specified by key.
        :param key: boolean flag represents the answer
        """
        pass

    @abstractmethod
    def get_nearest(self, key: str) -> (SpecNode, str):
        """
        Returns configuration specification value by key or nearest top-level presented if original does not exist.
        Value type is one of the SpecNode implementation.
        :param key: string represents path in configuration specification tree
        :returns pair consists of the nearest top-level presented value and rest path corresponding to non-existence part
        """
        pass

    @abstractmethod
    def get(self, key: str) -> SpecNode:
        """
        Returns configuration specification value by key or None if value not present.
        Value type is one of the SpecNode implementation.
        :param key: string represents path in configuration specification tree
        """
        pass

    def composite(self, key: str) -> CompositeSpecNode:
        """
        Returns CompositeSpecNode from configuration specification by key or None if value not present.
        :param key: string represents path in configuration specification tree
        """
        result = self.get(key)
        if isinstance(result, CompositeSpecNode):
            return result
        else:
            return None

    def list(self, key: str) -> ArraySpecNode:
        """
        Returns ArraySpecNode from configuration specification by key or None if value not present.
        :param key: string represents path in configuration specification tree
        """
        result = self.get(key)
        if isinstance(result, ArraySpecNode):
            return result
        else:
            return None

    def string(self, key: str) -> StringSpecNode:
        """
        Returns StringSpecNode from configuration specification by key or None if value not present.
        :param key: string represents path in configuration specification tree
        """
        result = self.get(key)
        if isinstance(result, StringSpecNode):
            return result
        else:
            return None

    def boolean(self, key: str) -> BooleanSpecNode:
        """
        Returns BooleanSpecNode from configuration specification by key or None if value not present.
        :param key: string represents path in configuration specification tree
        """
        result = self.get(key)
        if isinstance(result, BooleanSpecNode):
            return result
        else:
            return None

    def integer(self, key: str) -> IntegerSpecNode:
        """
        Returns IntegerSpecNode from configuration specification by key or None if value not present.
        :param key: string represents path in configuration specification tree
        """
        result = self.get(key)
        if isinstance(result, IntegerSpecNode):
            return result
        else:
            return None
