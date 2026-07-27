"""Local validation runner for the experimental FritzTAM branch stack."""

from __future__ import annotations

import argparse
import getpass
import sys
from typing import Any

from fritzconnection.lib.fritztam import FritzTAM


_PRIVATE_FIELD_PARTS = (
    'called',
    'caller',
    'name',
    'number',
    'path',
    'phone',
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            'Validate FritzTAM against a local FRITZ!Box. Read operations '
            'are the default; changes require --apply.'
        )
    )
    parser.add_argument('--address', default='fritz.box')
    parser.add_argument('--user', default=None)
    parser.add_argument('--port', type=int, default=None)
    parser.add_argument('--timeout', type=float, default=10.0)
    parser.add_argument('--use-tls', action='store_true')
    parser.add_argument(
        '--show-private',
        action='store_true',
        help='show caller names, numbers, and recording paths',
    )

    commands = parser.add_subparsers(dest='command', required=True)

    commands.add_parser('list', help='list configured answering machines')

    info = commands.add_parser('info', help='show one answering machine')
    info.add_argument('--tam-index', type=int, default=0)

    messages = commands.add_parser('messages', help='list voicemail metadata')
    messages.add_argument('--tam-index', type=int, default=0)
    messages.add_argument('--maximum', type=int, default=10)

    for name, help_text in (
        ('enable', 'enable one answering machine'),
        ('disable', 'disable one answering machine'),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument('--tam-index', type=int, required=True)
        command.add_argument('--apply', action='store_true')

    for name, help_text in (
        ('mark-read', 'mark one voicemail read'),
        ('mark-unread', 'mark one voicemail unread'),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument('--tam-index', type=int, required=True)
        command.add_argument('--message-index', type=int, required=True)
        command.add_argument('--apply', action='store_true')

    delete = commands.add_parser(
        'delete',
        help='permanently delete one voicemail',
    )
    delete.add_argument('--tam-index', type=int, required=True)
    delete.add_argument('--message-index', type=int, required=True)
    delete.add_argument('--apply', action='store_true')
    delete.add_argument(
        '--confirm',
        help='must equal DELETE:<tam-index>:<message-index>',
    )
    return parser


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


def _redacted(key: str, value: Any, show_private: bool) -> Any:
    if show_private:
        return value
    lowered = key.lower()
    if any(part in lowered for part in _PRIVATE_FIELD_PARTS):
        return '<redacted>' if value else value
    return value


def _print_info(info: dict, show_private: bool) -> None:
    for key in sorted(info):
        print(f'{key}: {_redacted(key, info[key], show_private)}')


def _list_tams(tam: FritzTAM) -> None:
    tam_list = tam.get_list()
    print(
        'running=', tam_list.running,
        'capacity=', tam_list.capacity,
        'status=', tam_list.status,
    )
    for item in tam_list:
        print(
            f'index={item.index} '
            f'enabled={item.enabled} '
            f'display={item.display} '
            f'name={item.name!r}'
        )


def _list_messages(
    tam: FritzTAM,
    tam_index: int,
    maximum: int,
    show_private: bool,
) -> None:
    messages = tam.get_messages(index=tam_index, maximum=maximum)
    print(f'{len(messages)} message(s) returned')
    for message in messages:
        values = [
            f'index={message.index}',
            f'tam={message.tam_index}',
            f'date={message.Date!r}',
            f'duration={message.Duration!r}',
            f'new={message.is_new}',
        ]
        if show_private:
            values.extend(
                [
                    f'name={message.Name!r}',
                    f'number={message.Number!r}',
                    f'called={message.Called!r}',
                    f'path={message.path!r}',
                ]
            )
        print(' '.join(values))


def _require_apply(args: argparse.Namespace, description: str) -> bool:
    if args.apply:
        return True
    print(f'DRY RUN: {description}')
    print('Repeat the command with --apply to make the change.')
    return False


def _run(args: argparse.Namespace, tam: FritzTAM) -> int:
    if args.command == 'list':
        _list_tams(tam)
        return 0

    if args.command == 'info':
        _print_info(tam.get_info(args.tam_index), args.show_private)
        return 0

    if args.command == 'messages':
        _list_messages(
            tam,
            args.tam_index,
            args.maximum,
            args.show_private,
        )
        return 0

    if args.command in ('enable', 'disable'):
        enabled = args.command == 'enable'
        description = (
            f'set answering machine {args.tam_index} '
            f'enabled={enabled}'
        )
        if _require_apply(args, description):
            tam.set_enabled(args.tam_index, enabled=enabled)
            print('Applied:', description)
        return 0

    if args.command in ('mark-read', 'mark-unread'):
        read = args.command == 'mark-read'
        description = (
            f'mark TAM {args.tam_index} message '
            f'{args.message_index} read={read}'
        )
        if _require_apply(args, description):
            tam.mark_message(
                args.tam_index,
                args.message_index,
                read=read,
            )
            print('Applied:', description)
        return 0

    if args.command == 'delete':
        description = (
            f'permanently delete TAM {args.tam_index} '
            f'message {args.message_index}'
        )
        if not _require_apply(args, description):
            return 0
        expected = f'DELETE:{args.tam_index}:{args.message_index}'
        if args.confirm != expected:
            print('Deletion refused.', file=sys.stderr)
            print(
                f'Use --confirm {expected!r} for this exact message.',
                file=sys.stderr,
            )
            return 2
        tam.delete_message(args.tam_index, args.message_index)
        print('Applied:', description)
        return 0

    raise AssertionError(args.command)


def main() -> int:
    args = _parser().parse_args()
    tam = _connect(args)
    return _run(args, tam)


if __name__ == '__main__':
    raise SystemExit(main())
