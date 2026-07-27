from xml.etree import ElementTree as etree

import pytest

from fritzconnection.lib import fritztam
from fritzconnection.lib.fritztam import FritzTAM


TAM_LIST_XML = """\
<List>
  <TAMRunning>1</TAMRunning>
  <Stick>0</Stick>
  <Status>0</Status>
  <Capacity>77</Capacity>
  <Item>
    <Index>0</Index>
    <Display>1</Display>
    <Enable>1</Enable>
    <Name>Answering machine</Name>
  </Item>
  <Item>
    <Index>1</Index>
    <Display>0</Display>
    <Enable>0</Enable>
    <Name></Name>
  </Item>
</List>
"""

MESSAGE_LIST_XML = """\
<Root>
  <Message>
    <Index>7</Index>
    <Tam>0</Tam>
    <Called>0123456789</Called>
    <Date>23.09.11 08:13</Date>
    <Duration>0:01</Duration>
    <Inbook>1</Inbook>
    <Name>Example Caller</Name>
    <New>0</New>
    <Number>555123456</Number>
    <Path>/data/tam/rec/rec.0.007</Path>
  </Message>
</Root>
"""


class FakeFritzConnection:
    def __init__(self):
        self.session = object()
        self.calls = []

    def call_action(self, service, actionname, **kwargs):
        self.calls.append((service, actionname, kwargs))
        if actionname == 'GetInfo':
            return {
                'NewEnable': True,
                'NewName': 'Answering machine',
            }
        if actionname == 'GetList':
            return {'NewTAMList': TAM_LIST_XML}
        if actionname == 'GetMessageList':
            return {
                'NewURL': (
                    'http://fritz.box/tam/messages.lua?'
                    'sid=0123456789abcdef&max=999'
                )
            }
        raise AssertionError(actionname)


@pytest.fixture()
def fc():
    return FakeFritzConnection()


def test_get_info_calls_tam_service(fc):
    tam = FritzTAM(fc=fc)

    result = tam.get_info(2)

    assert result['NewName'] == 'Answering machine'
    assert fc.calls == [
        ('X_AVM-DE_TAM1', 'GetInfo', {'NewIndex': 2})
    ]


def test_get_list_parses_global_and_item_information(fc):
    tam = FritzTAM(fc=fc)

    result = tam.get_list()

    assert result.running is True
    assert result.stick == 0
    assert result.status == 0
    assert result.capacity == 77
    assert len(result.items) == 2
    assert result.items[0].index == 0
    assert result.items[0].display is True
    assert result.items[0].enabled is True
    assert result.items[0].name == 'Answering machine'
    assert result.items[1].enabled is False


def test_get_messages_parses_message_list(monkeypatch, fc):
    requested = {}

    def fake_get_xml_root(url, session):
        requested['url'] = url
        requested['session'] = session
        return etree.fromstring(MESSAGE_LIST_XML)

    monkeypatch.setattr(fritztam, 'get_xml_root', fake_get_xml_root)
    tam = FritzTAM(fc=fc)

    messages = tam.get_messages(index=0, maximum=25)

    assert requested['url'].endswith(
        'sid=0123456789abcdef&max=25'
    )
    assert requested['session'] is fc.session
    assert len(messages) == 1
    message = messages[0]
    assert message.index == 7
    assert message.tam_index == 0
    assert message.in_phonebook is True
    assert message.is_new is True
    assert message.path == '/data/tam/rec/rec.0.007'


def test_get_message_list_url_uses_requested_index(fc):
    tam = FritzTAM(fc=fc)

    url = tam.get_message_list_url(3)

    assert url.startswith('http://fritz.box/')
    assert fc.calls == [
        ('X_AVM-DE_TAM1', 'GetMessageList', {'NewIndex': 3})
    ]
