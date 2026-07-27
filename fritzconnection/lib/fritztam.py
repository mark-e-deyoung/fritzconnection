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
    processor,
    process_node,
    InstanceAttributeFactory,
    Storage,
)
from ..core.utils import get_xml_root
from .fritzbase import AbstractLibraryBase


__all__ = ['FritzTAM', 'TAMList', 'TAMListItem', 'TAMMessage']


SERVICE = 'X_AVM-DE_TAM1'


def _boolean(value):
    """Convert a FRITZ!Box boolean value to bool."""
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


def _integer(value):
    """Convert a FRITZ!Box integer value to int or preserve None."""
    return None if value is None else int(value)


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
    Provides read-only access to telephone answering machines and their
    voicemail message lists.

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
        return _integer(self.Index)

    @property
    def display(self) -> bool:
        """Whether the answering machine is displayed in the web interface."""
        return _boolean(self.Display)

    @property
    def enabled(self) -> bool:
        """Whether the answering machine is enabled."""
        return _boolean(self.Enable)

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
        self.items = list()
        super().__init__(self.items)
        process_node(self, root)

    @property
    def running(self) -> bool:
        """Whether the answering-machine service is running."""
        return _boolean(self.TAMRunning)

    @property
    def stick(self) -> int | None:
        """USB storage state reported by the FRITZ!Box."""
        return _integer(self.Stick)

    @property
    def status(self) -> int | None:
        """Global answering-machine status bit field."""
        return _integer(self.Status)

    @property
    def capacity(self) -> int | None:
        """Remaining recording capacity in minutes."""
        return _integer(self.Capacity)

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
        return _integer(self.Index)

    @property
    def tam_index(self) -> int | None:
        """Index of the answering machine containing the message."""
        return _integer(self.Tam)

    @property
    def in_phonebook(self) -> bool:
        """Whether the caller is stored in a phonebook."""
        return _boolean(self.Inbook)

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
        self.messages = list()
        super().__init__(self.messages)
        process_node(self, root)
