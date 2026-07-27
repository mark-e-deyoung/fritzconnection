"""Automated live-router validation for the fork-only FritzTAM stack."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import getpass
import json
from pathlib import Path
import platform
import re
import sys
from typing import Any, Callable

from fritzconnection.lib.fritztam import FritzTAM


_SENSITIVE_QUERY = re.compile(
    r'(?i)(sid|password|passwd|token)=([^&\s]+)'
)
_MUTATING_MODES = {'message-state', 'tam-enable', 'delete'}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            'Run sanitized FritzTAM validation. Mutating modes are dry runs '
            'unless --apply and an exact confirmation are supplied.'
        )
    )
    parser.add_argument('--address', default='fritz.box')
    parser.add_argument('--user', default=None)
    parser.add_argument('--port', type=int, default=None)
    parser.add_argument('--timeout', type=float, default=10.0)
    parser.add_argument('--use-tls', action='store_true')
    parser.add_argument('--report', type=Path, default=None)

    modes = parser.add_subparsers(dest='mode', required=True)

    readonly = modes.add_parser(
        'readonly',
        help='validate TAM list, TAM info, and voicemail-list parsing',
    )
    readonly.add_argument('--tam-index', type=int, default=0)
    readonly.add_argument('--maximum', type=int, default=10)

    message = modes.add_parser(
        'message-state',
        help='toggle one message read state and restore the original state',
    )
    message.add_argument('--tam-index', type=int, required=True)
    message.add_argument('--message-index', type=int, required=True)
    message.add_argument('--apply', action='store_true')
    message.add_argument(
        '--confirm',
        help='must equal MARK:<tam-index>:<message-index>',
    )

    enable = modes.add_parser(
        'tam-enable',
        help='toggle one TAM enable state and restore the original state',
    )
    enable.add_argument('--tam-index', type=int, required=True)
    enable.add_argument('--apply', action='store_true')
    enable.add_argument(
        '--confirm',
        help='must equal TOGGLE-TAM:<tam-index>',
    )

    delete = modes.add_parser(
        'delete',
        help='delete one disposable voicemail and verify its absence',
    )
    delete.add_argument('--tam-index', type=int, required=True)
    delete.add_argument('--message-index', type=int, required=True)
    delete.add_argument('--apply', action='store_true')
    delete.add_argument(
        '--disposable',
        action='store_true',
        help='affirm that the selected voicemail is disposable',
    )
    delete.add_argument(
        '--confirm',
        help='must equal DELETE:<tam-index>:<message-index>',
    )
    return parser


def _confirmation(args: argparse.Namespace) -> str | None:
    if args.mode == 'message-state':
        return f'MARK:{args.tam_index}:{args.message_index}'
    if args.mode == 'tam-enable':
        return f'TOGGLE-TAM:{args.tam_index}'
    if args.mode == 'delete':
        return f'DELETE:{args.tam_index}:{args.message_index}'
    return None


def _preflight(args: argparse.Namespace) -> int | None:
    if args.mode not in _MUTATING_MODES:
        return None
    expected = _confirmation(args)
    if not args.apply:
        print(f'DRY RUN: {args.mode}')
        print(f'Repeat with --apply --confirm {expected!r}.')
        if args.mode == 'delete':
            print('Deletion also requires --disposable.')
        return 0
    if args.mode == 'delete' and not args.disposable:
        print('Deletion refused: --disposable is required.', file=sys.stderr)
        return 2
    if args.confirm != expected:
        print('Operation refused.', file=sys.stderr)
        print(f'Use --confirm {expected!r}.', file=sys.stderr)
        return 2
    return None


def _connect(args: argparse.Namespace) -> FritzTAM:
    password = getpass.getpass('FRITZ!Box password: ')
    options: dict[str, Any] = {
        'address': args.address,
        'user': args.user,
        'password': password,
        'timeout': args.timeout,
        'use_tls': args.use_tls,
    }
    if args.port is not None:
        options['port'] = args.port
    return FritzTAM(**options)


def _safe_error(error: Exception) -> dict[str, str]:
    message = _SENSITIVE_QUERY.sub(r'\1=<redacted>', str(error))
    return {'type': type(error).__name__, 'message': message[:500]}


def _report_path(args: argparse.Namespace) -> Path:
    if args.report is not None:
        return args.report
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    return Path('.local-validation') / (
        f'fritztam-{args.mode}-{timestamp}.json'
    )


def _new_report(args: argparse.Namespace) -> dict[str, Any]:
    return {
        'schema_version': 1,
        'mode': args.mode,
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'environment': {
            'platform': platform.platform(),
            'python': platform.python_version(),
        },
        'target': {
            'address': '<configured>',
            'tam_index': getattr(args, 'tam_index', None),
            'message_index': getattr(args, 'message_index', None),
        },
        'steps': [],
        'overall': 'pending',
    }


def _write_report(args: argparse.Namespace, report: dict[str, Any]) -> None:
    path = _report_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + '\n',
        encoding='utf-8',
    )
    print(f'Sanitized report: {path}')


def _step(
    report: dict[str, Any],
    name: str,
    operation: Callable[[], dict[str, Any]],
) -> bool:
    try:
        details = operation()
    except Exception as error:
        report['steps'].append(
            {'name': name, 'status': 'fail', 'error': _safe_error(error)}
        )
        print(f'FAIL: {name}: {type(error).__name__}')
        return False
    report['steps'].append(
        {'name': name, 'status': 'pass', 'details': details}
    )
    print(f'PASS: {name}')
    return True


def _find_tam(tam: FritzTAM, tam_index: int):
    for item in tam.get_list():
        if item.index == tam_index:
            return item
    raise LookupError(f'answering machine {tam_index} was not returned')


def _find_message(tam: FritzTAM, tam_index: int, message_index: int):
    for message in tam.get_messages(index=tam_index, maximum=999):
        if message.index == message_index:
            return message
    raise LookupError(
        f'message {message_index} was not returned for TAM {tam_index}'
    )


def _readonly(args: argparse.Namespace, tam: FritzTAM) -> int:
    report = _new_report(args)

    def tam_list() -> dict[str, Any]:
        result = tam.get_list()
        items = list(result)
        return {
            'item_count': len(items),
            'selected_tam_present': any(
                item.index == args.tam_index for item in items
            ),
            'indices_parsed': all(item.index is not None for item in items),
            'running_type': type(result.running).__name__,
            'capacity_type': type(result.capacity).__name__,
            'status_type': type(result.status).__name__,
        }

    def tam_info() -> dict[str, Any]:
        result = tam.get_info(args.tam_index)
        return {
            'returned_key_count': len(result),
            'returned_keys': sorted(result),
        }

    def message_list() -> dict[str, Any]:
        messages = tam.get_messages(
            index=args.tam_index,
            maximum=args.maximum,
        )
        return {
            'message_count': len(messages),
            'indices_parsed': all(
                message.index is not None for message in messages
            ),
            'tam_indices_consistent': all(
                message.tam_index in (None, args.tam_index)
                for message in messages
            ),
            'new_count': sum(message.is_new for message in messages),
            'recording_paths_present': sum(
                bool(message.path) for message in messages
            ),
            'empty_list_observed': not messages,
        }

    passed = all(
        (
            _step(report, 'GetList', tam_list),
            _step(report, 'GetInfo', tam_info),
            _step(report, 'GetMessageList', message_list),
        )
    )
    report['overall'] = 'pass' if passed else 'fail'
    _write_report(args, report)
    return 0 if passed else 1


def _reversible(
    args: argparse.Namespace,
    tam: FritzTAM,
    label: str,
    get_state: Callable[[], bool],
    set_state: Callable[[bool], None],
) -> int:
    report = _new_report(args)
    original: bool | None = None
    restored = False
    try:
        original = get_state()
        target = not original
        set_state(target)
        if get_state() != target:
            raise RuntimeError(f'{label} did not change as requested')
        set_state(original)
        restored = get_state() == original
        if not restored:
            raise RuntimeError(f'{label} was not restored')
        report['steps'].append(
            {
                'name': f'toggle-and-restore-{label}',
                'status': 'pass',
                'details': {
                    'original': original,
                    'target': target,
                    'restored': restored,
                },
            }
        )
        report['overall'] = 'pass'
        print(f'PASS: {label} toggled, verified, and restored')
        code = 0
    except Exception as error:
        report['steps'].append(
            {
                'name': f'toggle-and-restore-{label}',
                'status': 'fail',
                'error': _safe_error(error),
            }
        )
        report['overall'] = 'fail'
        print(f'FAIL: {label}: {type(error).__name__}', file=sys.stderr)
        code = 1
    finally:
        if original is not None and not restored:
            try:
                set_state(original)
                restored = get_state() == original
                report['restoration_after_failure'] = (
                    'pass' if restored else 'fail'
                )
            except Exception as error:
                report['restoration_after_failure'] = {
                    'status': 'fail',
                    'error': _safe_error(error),
                }
        _write_report(args, report)
    return code


def _message_state(args: argparse.Namespace, tam: FritzTAM) -> int:
    def get_state() -> bool:
        message = _find_message(
            tam, args.tam_index, args.message_index
        )
        return not message.is_new

    def set_state(read: bool) -> None:
        tam.mark_message(
            args.tam_index,
            args.message_index,
            read=read,
        )

    return _reversible(args, tam, 'message-read-state', get_state, set_state)


def _tam_enable(args: argparse.Namespace, tam: FritzTAM) -> int:
    def get_state() -> bool:
        return _find_tam(tam, args.tam_index).enabled

    def set_state(enabled: bool) -> None:
        tam.set_enabled(args.tam_index, enabled=enabled)

    return _reversible(args, tam, 'tam-enable-state', get_state, set_state)


def _delete(args: argparse.Namespace, tam: FritzTAM) -> int:
    report = _new_report(args)
    try:
        _find_message(tam, args.tam_index, args.message_index)
        tam.delete_message(args.tam_index, args.message_index)
        try:
            _find_message(tam, args.tam_index, args.message_index)
        except LookupError:
            pass
        else:
            raise RuntimeError('deleted message is still present')
        report['steps'].append(
            {
                'name': 'delete-and-verify-message',
                'status': 'pass',
                'details': {
                    'disposable_acknowledged': True,
                    'message_absent_after_delete': True,
                },
            }
        )
        report['overall'] = 'pass'
        print('PASS: disposable message deleted and absence verified')
        code = 0
    except Exception as error:
        report['steps'].append(
            {
                'name': 'delete-and-verify-message',
                'status': 'fail',
                'error': _safe_error(error),
            }
        )
        report['overall'] = 'fail'
        print(
            f'FAIL: deletion validation: {type(error).__name__}',
            file=sys.stderr,
        )
        code = 1
    _write_report(args, report)
    return code


def _run(args: argparse.Namespace, tam: FritzTAM) -> int:
    if args.mode == 'readonly':
        return _readonly(args, tam)
    if args.mode == 'message-state':
        return _message_state(args, tam)
    if args.mode == 'tam-enable':
        return _tam_enable(args, tam)
    if args.mode == 'delete':
        return _delete(args, tam)
    raise AssertionError(args.mode)


def main() -> int:
    args = _parser().parse_args()
    preflight = _preflight(args)
    if preflight is not None:
        return preflight
    return _run(args, _connect(args))


if __name__ == '__main__':
    raise SystemExit(main())
