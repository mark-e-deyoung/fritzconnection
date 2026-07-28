"""
Module to access telephone answering machines and voicemail messages.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)


from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from xml.etree import ElementTree as etree

from ..core.processor import (
    InstanceAttributeFactory,
    Storage,
    process_node,
    processor,
)
from ..core.utils import get_boolean_from_string, get_xml_root
from .fritzbase import AbstractLibraryBase

__all__ = ['FritzTAM', 'TAMList', 'TAMListItem', 'TAMMessage']


SERVICE = 'X_AVM-DE_TAM1'


def _set_url_parameter(url, name, value):
    """Return *url* with one query parameter replaced."""
    parts = urlsplit(url)
    parameters = dict(parse_qsl(parts.query, keep_blank_values=True))
    parameters[name] = str(value)
    query = urlencode(parameters)
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, query, parts.fragment)
    )


class FritzTAM(AbstractLibraryBase):
    """
    Provides access to telephone answering machines and their voicemail
    message lists.

    All parameters are optional. If given, they have the following meaning:
    `fc` is an instance of FritzConnection, `address` the ip of the
    FRITZ!Box, `port` the port to connect to, `user` the username,
    `password` the password, `timeout` a timeout as floating point number
    in seconds, `use_tls` a boolean indicating to use TLS (default False).
    """

    def _action(self, actionname, **kwargs):
        return self.fc.call_action(SERVICE, actionname, **kwargs)

    def get_info(self, index: int = 0) -> dict:
        """
        Return information about the answering machine selected by *index*.
        """
        return self._action('GetInfo', NewIndex=index)

    def get_list(self) -> TAMList:
        """
        Return global and per-answering-machine information as a TAMList.
        """
        result = self._action('GetList')
        root = etree.fromstring(result['NewTAMList'])
        return TAMList(root)

    def get_message_list_url(self, index: int = 0) -> str:
        """
        Return the temporary URL for the message list of answering machine
        *index*.
        """
        result = self._action('GetMessageList', NewIndex=index)
        return result['NewURL']

    def get_messages(
        self,
        index: int = 0,
        maximum: int | None = None,
    ) -> list[TAMMessage]:
        """
        Return voicemail messages for answering machine *index*.

        If *maximum* is provided, at most that number of messages is
        requested from the FRITZ!Box.
        """
        url = self.get_message_list_url(index)
        if maximum is not None:
            url = _set_url_parameter(url, 'max', maximum)
        root = get_xml_root(url, session=self.fc.session)
        return TAMMessageCollection(root).messages

    def mark_message(
        self,
        index: int,
        message_index: int,
        read: bool = True,
    ) -> None:
        """
        Mark one voicemail message as read or unread.

        *index* selects the answering machine and *message_index* is the
        stable index from the message list. If *read* is False, the message
        is marked as unread.
        """
        self._action(
            'MarkMessage',
            NewIndex=index,
            NewMessageIndex=message_index,
            NewMarkedAsRead=not read,
        )


@processor
class TAMListItem:
    """Information about one configured answering machine."""

    def __init__(self):
        self.Index = None
        self.Display = None
        self.Enable = None
        self.Name = None

    @property
    def index(self) -> int | None:
        """Integer answering-machine index."""
        if self.Index is None:
            return None
        return int(self.Index)

    @property
    def display(self) -> bool:
        """Whether the answering machine is displayed in the web interface."""
        return get_boolean_from_string(self.Display, default=False)

    @property
    def enabled(self) -> bool:
        """Whether the answering machine is enabled."""
        return get_boolean_from_string(self.Enable, default=False)

    @property
    def name(self) -> str | None:
        """Configured answering-machine name."""
        return self.Name


@processor
class TAMList(Storage):
    """Global and per-answering-machine information returned by GetList."""

    Item = InstanceAttributeFactory(TAMListItem)

    def __init__(self, root):
        self.TAMRunning = None
        self.Stick = None
        self.Status = None
        self.Capacity = None
        self.items = []
        super().__init__(self.items)
        process_node(self, root)

    @property
    def running(self) -> bool:
        """Whether the answering-machine service is running."""
        return get_boolean_from_string(self.TAMRunning, default=False)

    @property
    def stick(self) -> int | None:
        """USB storage state reported by the FRITZ!Box."""
        if self.Stick is None:
            return None
        return int(self.Stick)

    @property
    def status(self) -> int | None:
        """Global answering-machine status bit field."""
        if self.Status is None:
            return None
        return int(self.Status)

    @property
    def capacity(self) -> int | None:
        """Remaining recording capacity in minutes."""
        if self.Capacity is None:
            return None
        return int(self.Capacity)

    def __iter__(self):
        return iter(self.items)


@processor
class TAMMessage:
    """One voicemail message from a FRITZ!Box answering machine."""

    def __init__(self):
        self.Index = None
        self.Tam = None
        self.Called = None
        self.Date = None
        self.Duration = None
        self.Inbook = None
        self.Name = None
        self.New = None
        self.Number = None
        self.Path = None

    @property
    def index(self) -> int | None:
        """Stable message index used by message actions."""
        if self.Index is None:
            return None
        return int(self.Index)

    @property
    def tam_index(self) -> int | None:
        """Index of the answering machine containing the message."""
        if self.Tam is None:
            return None
        return int(self.Tam)

    @property
    def in_phonebook(self) -> bool:
        """Whether the caller is stored in a phonebook."""
        return get_boolean_from_string(self.Inbook, default=False)

    @property
    def is_new(self) -> bool:
        """
        Whether the message is new.

        FRITZ!Box message lists use 0 for a new message and 1 for a message
        that has already been marked.
        """
        return str(self.New) == '0'

    @property
    def path(self) -> str | None:
        """Router-relative path of the voicemail recording."""
        return self.Path


class TAMMessageCollection(Storage):
    """Container used while parsing a voicemail message list."""

    Message = InstanceAttributeFactory(TAMMessage)

    def __init__(self, root):
        self.messages = []
        super().__init__(self.messages)
        process_node(self, root)
