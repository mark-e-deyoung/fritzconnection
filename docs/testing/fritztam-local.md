# Local FritzTAM validation

This document and `tools/fritztam_local.py` are fork-only integration aids. They
are not intended for an upstream pull request.

## Checkout and install on Windows 11

```powershell
git clone https://github.com/mark-e-deyoung/fritzconnection.git
cd fritzconnection
git fetch origin
git switch integration/tam-local-test

py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e . pytest
```

The integration branch contains the complete stacked TAM implementation. The
individual draft PRs remain separated for review.

## Run the focused tests

```powershell
python -m pytest fritzconnection/tests/test_fritztam*.py -q
```

Expected result for the current stack:

```text
9 passed
```

## Router prerequisites

- Enable TR-064 access on the home network.
- Use a FRITZ!Box account with the `Phone` permission.
- Configure at least one answering machine before testing message operations.
- Do not publish test output containing caller names, telephone numbers, or
  recording paths.

The runner prompts for the password using `getpass`; it does not accept a
password command-line option and therefore does not place the password in shell
history.

## Read-only checks

List answering machines:

```powershell
python tools/fritztam_local.py --address fritz.box list
```

Inspect answering machine zero. Private fields are redacted by default:

```powershell
python tools/fritztam_local.py --address fritz.box info --tam-index 0
```

List up to ten voicemail records:

```powershell
python tools/fritztam_local.py --address fritz.box messages `
    --tam-index 0 --maximum 10
```

To show caller names, numbers, and recording paths locally, place the global
option before the subcommand:

```powershell
python tools/fritztam_local.py --address fritz.box --show-private messages `
    --tam-index 0 --maximum 10
```

## Reversible changes

Mutation commands are dry runs unless `--apply` is present.

```powershell
python tools/fritztam_local.py enable --tam-index 0
python tools/fritztam_local.py enable --tam-index 0 --apply
python tools/fritztam_local.py disable --tam-index 0 --apply
```

Mark a message read or unread using the stable message index shown by the
`messages` command:

```powershell
python tools/fritztam_local.py mark-read `
    --tam-index 0 --message-index 7 --apply

python tools/fritztam_local.py mark-unread `
    --tam-index 0 --message-index 7 --apply
```

After each mutation, rerun `list`, `info`, or `messages` to verify the observed
router state.

## Destructive deletion test

Only test deletion using a disposable voicemail message created for this
purpose. The command requires both `--apply` and a confirmation string bound to
the exact TAM and message indices.

Dry run:

```powershell
python tools/fritztam_local.py delete `
    --tam-index 0 --message-index 7
```

Apply to that exact message:

```powershell
python tools/fritztam_local.py delete `
    --tam-index 0 --message-index 7 --apply `
    --confirm DELETE:0:7
```

Deletion is permanent. Confirm the message is the disposable test recording by
using `messages --show-private` before running the deletion command.

## Sanitized validation record

Record only:

```text
Router model:
FRITZ!OS version:
Python version:
Read-only list: pass/fail
Message-list parsing: pass/fail
Mark read/unread: pass/fail/not tested
Enable/disable: pass/fail/not tested
Delete disposable message: pass/fail/not tested
Observed limitations:
```

Do not record credentials, SIDs, serial numbers, telephone numbers, contact
names, MAC addresses, public IP addresses, or recording paths.
