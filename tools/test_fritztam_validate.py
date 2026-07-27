from argparse import Namespace
import json

from tools import fritztam_validate as validator


class Item:
    def __init__(self, index=0, enabled=True):
        self.index = index
        self.enabled = enabled


class TamList:
    running = True
    capacity = 42
    status = 0

    def __init__(self, item):
        self._items = [item]

    def __iter__(self):
        return iter(self._items)


class Message:
    def __init__(self, index=7, tam_index=0, is_new=True):
        self.index = index
        self.tam_index = tam_index
        self.is_new = is_new
        self.path = '/private/path?sid=0123456789abcdef'


class FakeTam:
    def __init__(self):
        self.item = Item()
        self.messages = [Message()]

    def get_list(self):
        return TamList(self.item)

    def get_info(self, index):
        assert index == self.item.index
        return {'NewEnable': self.item.enabled, 'NewName': 'Private'}

    def get_messages(self, index, maximum):
        assert index == self.item.index
        return list(self.messages[:maximum])

    def mark_message(self, index, message_index, read=True):
        assert index == self.item.index
        for message in self.messages:
            if message.index == message_index:
                message.is_new = not read
                return
        raise LookupError(message_index)

    def set_enabled(self, index, enabled=True):
        assert index == self.item.index
        self.item.enabled = enabled

    def delete_message(self, index, message_index):
        assert index == self.item.index
        self.messages = [
            message for message in self.messages
            if message.index != message_index
        ]


def args_for(mode, report):
    return Namespace(
        mode=mode,
        address='fritz.box',
        user=None,
        port=None,
        timeout=10.0,
        use_tls=False,
        report=report,
        tam_index=0,
        message_index=7,
        maximum=10,
        apply=True,
        disposable=False,
        confirm=None,
    )


def test_readonly_report_is_sanitized(tmp_path):
    report = tmp_path / 'readonly.json'
    args = args_for('readonly', report)

    assert validator._run(args, FakeTam()) == 0

    text = report.read_text(encoding='utf-8')
    data = json.loads(text)
    assert data['overall'] == 'pass'
    assert 'Private' not in text
    assert '0123456789abcdef' not in text
    assert 'fritz.box' not in text


def test_message_state_is_restored(tmp_path):
    tam = FakeTam()
    args = args_for('message-state', tmp_path / 'message.json')
    args.confirm = 'MARK:0:7'

    assert validator._preflight(args) is None
    assert validator._run(args, tam) == 0
    assert tam.messages[0].is_new is True


def test_tam_enable_state_is_restored(tmp_path):
    tam = FakeTam()
    args = args_for('tam-enable', tmp_path / 'enable.json')
    args.confirm = 'TOGGLE-TAM:0'

    assert validator._preflight(args) is None
    assert validator._run(args, tam) == 0
    assert tam.item.enabled is True


def test_delete_requires_disposable_before_connect(tmp_path):
    args = args_for('delete', tmp_path / 'delete.json')
    args.confirm = 'DELETE:0:7'

    assert validator._preflight(args) == 2


def test_delete_removes_only_selected_message(tmp_path):
    tam = FakeTam()
    args = args_for('delete', tmp_path / 'delete.json')
    args.disposable = True
    args.confirm = 'DELETE:0:7'

    assert validator._preflight(args) is None
    assert validator._run(args, tam) == 0
    assert tam.messages == []


def test_safe_error_redacts_sensitive_query_values():
    error = RuntimeError(
        'failed http://fritz.box/x?sid=0123456789abcdef&token=secret'
    )

    safe = validator._safe_error(error)

    assert '0123456789abcdef' not in safe['message']
    assert 'secret' not in safe['message']
    assert 'sid=<redacted>' in safe['message']
