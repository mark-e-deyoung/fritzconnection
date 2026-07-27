# Local FritzTAM validation

This document and the scripts under `tools/` are fork-only integration aids.
They are not intended for an upstream pull request.

## Checkout and install on Windows 11

```powershell
git clone https://github.com/mark-e-deyoung/fritzconnection.git
cd fritzconnection
git fetch origin
git switch integration/tam-local-test
git pull --ff-only origin integration/tam-local-test

py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e . pytest
```

The integration branch contains the complete stacked TAM implementation. The
individual draft PRs remain separated for review.

## Run the focused tests

Run the feature tests:

```powershell
python -m pytest fritzconnection/tests/test_fritztam*.py -q
```

Expected result:

```text
9 passed
```

Run the automation safety tests:

```powershell
python -m pytest tools/test_fritztam_validate.py -q
```

Expected result:

```text
6 passed
```

## Router prerequisites

- Enable TR-064 access on the home network.
- Use a FRITZ!Box account with the `Phone` permission.
- Configure at least one answering machine before testing message operations.
- Do not publish output containing caller names, telephone numbers, or recording
  paths.

Both runners prompt for the password using `getpass`. Neither accepts a password
command-line argument, so the password is not placed in shell history.

## Automated read-only validation

`tools/fritztam_validate.py` runs the TAM list, TAM information, and voicemail
message-list checks in one authenticated session. It prompts for the password
once and writes a sanitized JSON report.

```powershell
python tools/fritztam_validate.py --address fritz.box readonly `
    --tam-index 0 --maximum 10
```

In Claude Code, the same command can be launched with the shell prefix:

```text
! python tools/fritztam_validate.py --address fritz.box readonly --tam-index 0 --maximum 10
```

The command validates:

- `GetList` parsing and TAM index handling
- `GetInfo` response shape
- `GetMessageList` retrieval and message-list parsing
- stable message-index parsing
- TAM index consistency
- new/read-state parsing
- empty message-list behavior when an empty list is observed

The report is written under `.local-validation/` by default. That directory is
ignored by Git. The report contains counts, field names, state booleans, and
pass/fail results. It does not contain the configured router address, password,
SID, caller name, telephone number, or recording path.

To select a specific report path, put the global option before the mode:

```powershell
python tools/fritztam_validate.py `
    --report C:\Temp\fritztam-readonly.json `
    readonly --tam-index 0 --maximum 10
```

If any read-only step fails, stop mutation testing and repair the read-only PR
first.

## Automated reversible message-state validation

The `message-state` mode determines the current state, toggles it, verifies the
change, restores the original state, and verifies restoration.

First run the dry run. It exits before authentication:

```powershell
python tools/fritztam_validate.py message-state `
    --tam-index 0 --message-index 7
```

Apply the reversible test only after confirming the stable message index:

```powershell
python tools/fritztam_validate.py message-state `
    --tam-index 0 --message-index 7 `
    --apply --confirm MARK:0:7
```

The validator attempts restoration in a `finally` block if a verification step
fails. Review the generated report for `restoration_after_failure` whenever the
command exits nonzero.

## Automated reversible TAM enable validation

The `tam-enable` mode records the current enabled state, toggles it, verifies the
change, restores the original state, and verifies restoration.

Dry run:

```powershell
python tools/fritztam_validate.py tam-enable --tam-index 0
```

Apply:

```powershell
python tools/fritztam_validate.py tam-enable `
    --tam-index 0 --apply --confirm TOGGLE-TAM:0
```

Do not use this mode on a TAM whose temporary interruption would cause an
operational problem.

## Optional automated deletion validation

Deletion is permanent and is not required to validate the first three PRs. Use
only a voicemail created specifically for disposal testing.

Dry run:

```powershell
python tools/fritztam_validate.py delete `
    --tam-index 0 --message-index 7
```

Apply to that exact disposable message:

```powershell
python tools/fritztam_validate.py delete `
    --tam-index 0 --message-index 7 `
    --apply --disposable --confirm DELETE:0:7
```

The validator confirms that the exact stable message index exists before the
delete action and that it is absent afterward. It cannot determine whether the
message is actually disposable; the operator remains responsible for that
judgment.

## Manual inspection runner

`tools/fritztam_local.py` remains available for individual commands and local
inspection. Private message fields are hidden unless `--show-private` is used.

List answering machines:

```powershell
python tools/fritztam_local.py --address fritz.box list
```

Inspect answering machine zero:

```powershell
python tools/fritztam_local.py --address fritz.box info --tam-index 0
```

List up to ten voicemail records:

```powershell
python tools/fritztam_local.py --address fritz.box messages `
    --tam-index 0 --maximum 10
```

Show caller names, numbers, and recording paths locally:

```powershell
python tools/fritztam_local.py --address fritz.box --show-private messages `
    --tam-index 0 --maximum 10
```

Do not paste private output into an agent session, issue, pull request, or test
report.

## Sanitized validation record

The generated JSON reports provide the machine-readable record. A human summary
should contain only:

```text
Router model:
FRITZ!OS version:
Python version:
Read-only list: pass/fail
TAM information: pass/fail
Message-list parsing: pass/fail
Mark read/unread: pass/fail/not tested
Enable/disable: pass/fail/not tested
Original state restored: pass/fail/not applicable
Delete disposable message: pass/fail/not tested
Observed limitations:
```

Do not record credentials, SIDs, serial numbers, telephone numbers, contact
names, MAC addresses, public IP addresses, or recording paths.
