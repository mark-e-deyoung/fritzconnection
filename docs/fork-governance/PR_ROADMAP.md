# Focused Upstream PR Roadmap

This roadmap turns the fork's contribution doctrine into a controlled sequence of
small, human-reviewable proposals for `kbr/fritzconnection`.

The roadmap is intentionally conservative. It is not a commitment to implement
all listed FRITZ!OS capabilities. Every candidate remains conditional on a
specific user need, upstream maintainer interest, protocol evidence, and the
ability to produce a small sustainable diff.

## Portfolio limits

The fork will maintain at most:

- one active upstream feature PR;
- one next candidate in maintainer-discussion or design-review status; and
- one experimental research track that is not represented as production-ready.

A later feature does not begin implementation merely because an earlier feature
was coded. It begins only after reviewing upstream feedback and deciding that the
next contribution remains useful and appropriately scoped.

No feature candidate may:

- use API coverage as its sole justification;
- require a repository-wide redesign;
- introduce a new runtime dependency without prior maintainer agreement;
- modify `fritzconnection/core/` as a convenience for one feature;
- combine documented and undocumented interfaces in one PR;
- include a CLI unless requested by the maintainer;
- bundle unrelated cleanup, typing, formatting, or packaging changes; or
- claim router support based only on mocked tests.

## Candidate states

Each candidate is assigned one state:

| State | Meaning |
| --- | --- |
| `research` | Verify need, interface, existing issues, and project fit. No production code. |
| `discussion` | Present the smallest proposal to upstream and confirm the target branch. |
| `approved-to-implement` | Scope and branch are sufficiently clear to start a feature branch. |
| `implementation` | Produce the smallest code, test, and documentation diff. |
| `validation` | Run repository checks and identified live-router tests. |
| `draft-pr` | Upstream draft PR is open and awaiting review. |
| `complete` | Accepted, declined, or explicitly retained outside upstream. |
| `deferred` | Valuable but not currently justified or maintainable. |

Only one candidate may be in `implementation`, `validation`, or `draft-pr` at a
time.

## Target-branch policy

The upstream base branch must be confirmed for each candidate before code is
written.

- Small fixes intended for the stable release may target `master` only when that
  matches upstream practice.
- New feature work should target the current development branch selected by the
  maintainer.
- A feature branch must begin directly from the confirmed upstream base.
- A candidate must be rebased onto the current upstream base before PR creation.

The roadmap does not assume that a branch name remains permanent.

## Sequence overview

| Order | Candidate | Interface | Default status | Core change |
| ---: | --- | --- | --- | --- |
| 0 | Upstream alignment for answering-machine support | TR-064 | discussion | none |
| 1 | Read-only `FritzTAM` wrapper | TR-064 | first candidate | none |
| 2 | Limited TAM state changes | TR-064 | conditional | none |
| 3 | Lossless phonebook contact access | TR-064 | conditional | none |
| 4 | Local phonebook contact mutation | TR-064 | conditional | none |
| 5 | Read-only host-filter information | TR-064 | conditional | none |
| 6 | Explicit device block/unblock | TR-064 | conditional | none |

The following remain research tracks rather than scheduled upstream PRs:

- Smart Home REST support;
- internet-radio management;
- WireGuard web-interface operations;
- internal statistics and diagnostics;
- system restore and firmware installation; and
- broad VoIP account provisioning.

## Candidate 0: upstream alignment for answering-machine support

### Goal

Ask whether upstream wants a small, read-only high-level wrapper for the official
answering-machine service and confirm the correct target branch and preferred
return style.

### Deliverable

An upstream issue or discussion containing:

- the demonstrated user need;
- the official service and actions involved;
- the nearest existing modules, especially `fritzcall.py` and
  `fritzphonebook.py`;
- a proposed file-level diff;
- explicit exclusions; and
- questions that materially affect implementation.

### Explicit exclusions

- no code;
- no voicemail deletion;
- no enable/disable operation;
- no audio-download helper;
- no CLI;
- no core or transport changes; and
- no undocumented web-interface calls.

### Go/no-go gate

Proceed only when the target branch and general scope are sufficiently clear.
Silence from upstream is not automatic approval to create a large PR. A very
small proof may be prepared in the fork, but it must remain a draft and preserve
all exclusions.

## Candidate 1: read-only `FritzTAM` wrapper

### User problem

The low-level API can access the answering-machine service, but users lack a
small repository-native wrapper for discovering configured answering machines
and reading their message metadata.

### Proposed branch

`feature/tam-read-only`

The branch must start directly from the confirmed upstream base.

### Intended production diff

```text
fritzconnection/lib/fritztam.py
fritzconnection/tests/test_fritztam.py
docs/sources/library_modules.rst
```

Additional sanitized XML test data may be added under the repository's existing
test-fixture structure when necessary.

### Minimum public surface

The exact names should be confirmed against upstream conventions, but the first
increment should support only:

- retrieving information for a specifically identified answering machine;
- discovering the available answering-machine indices when the advertised API
  provides a reliable method; and
- retrieving and parsing message-list metadata.

Return types should follow the nearest existing module. A new data-model framework
must not be introduced. If the existing `Storage` and processor patterns are the
closest fit for XML message lists, use them narrowly; otherwise return direct,
documented dictionaries.

### Explicit exclusions

- changing answering-machine configuration;
- marking messages read or unread;
- deleting messages;
- bulk operations;
- downloading recordings to disk;
- background polling;
- event subscriptions;
- CLI commands;
- changes to authentication or HTTP transport; and
- any undocumented endpoint.

### Test requirements

Tests must cover:

- successful information retrieval;
- parsing a realistic sanitized message list;
- an empty message list;
- missing optional fields;
- malformed or incomplete XML where existing project behavior permits a clear
  failure expectation; and
- correct service/action arguments through mocks.

A read-only live-router validation should record only router model, FRITZ!OS
version, service/action tested, and sanitized outcome.

### Size and quality gate

Pause for redesign when the candidate:

- needs more than one new high-level module;
- changes core code;
- introduces a dependency;
- requires a generic abstraction not used by the feature itself;
- includes mutation for convenience; or
- cannot be explained comfortably in one focused review.

### Completion gate

Candidate 1 is complete only after upstream accepts, declines, or gives enough
feedback to determine whether follow-on TAM work is welcome. Candidate 2 must not
begin before that evaluation.

## Candidate 2: limited TAM state changes

### Status

Conditional on upstream response to Candidate 1.

### Proposed branch

`feature/tam-message-state`

This branch should start from the upstream base after Candidate 1 is merged. It
should not stack on an unmerged PR unless the maintainer specifically requests a
stacked review.

### Candidate scope

Choose only the smallest state-changing operation requested by upstream, such as:

- enabling or disabling one specifically identified answering machine; or
- changing the read state of one specifically identified message.

These concerns may need separate PRs. Do not combine them merely because they use
the same service.

### Safety rules

- Require explicit answering-machine and message identifiers.
- Provide no bulk mutation method.
- Do not infer a target from list order when the API provides a stronger ID.
- Validate arguments before sending a mutation.
- Test the exact action and argument mapping.
- Record live validation for every mutating operation.

### Exclusions

Message deletion remains excluded unless separately requested and discussed.

## Candidate 3: lossless phonebook contact access

### Rationale

The current high-level phonebook helpers are read-only and some convenience
forms can collapse duplicate names. Before proposing write support, establish a
lossless, repository-compatible way to access contacts and their stable
identifiers.

### Proposed branch

`feature/phonebook-lossless-contacts`

### Candidate scope

A narrow read-only enhancement may expose existing parsed contact entries without
keying them solely by display name. It should preserve current public methods and
backward compatibility.

### Explicit exclusions

- no contact creation or deletion;
- no call-block management;
- no DECT handset assignment;
- no online-phonebook synchronization;
- no replacement of the existing parser; and
- no broad contact data model.

### Gate

Do not proceed when the existing `get_all_name_numbers()` API already meets the
demonstrated need. A new method must provide a concrete capability that cannot be
cleanly obtained today.

## Candidate 4: local phonebook contact mutation

### Status

Conditional on upstream acceptance of the contact-access design and explicit
maintainer interest in write operations.

### Candidate decomposition

Prefer separate PRs for:

1. create or update one local contact; and
2. delete one local contact by stable identifier.

Do not mix local phonebook CRUD with call blocking, online synchronization, or
handset assignment.

### Safety and sustainability

- Support only local phonebooks whose documented interface is verified.
- Preserve fields not intentionally changed when the API contract permits it.
- Require stable identifiers for update and deletion.
- Refuse ambiguous name-only mutation.
- Include round-trip tests against sanitized XML fixtures.
- Do not attempt a general contact synchronization framework.

## Candidate 5: read-only host-filter information

### Goal

Expose a specific, documented host-filter query needed for automation without
creating a general parental-control framework.

### Proposed branch

`feature/host-filter-read-only`

### Candidate scope

The exact method must be selected from a demonstrated use case and the service
advertised by the test router. Possible read-only information includes current
access state or available filter/profile data.

### Explicit exclusions

- no profile editor;
- no scheduling model;
- no ticket lifecycle framework;
- no undocumented profile assignment;
- no host discovery duplication; and
- no core networking changes.

## Candidate 6: explicit device block or unblock

### Status

Conditional on Candidate 5 and a demonstrated operational need.

### Candidate scope

One explicit, documented operation that changes WAN access for a specifically
identified device or address.

### Safety requirements

- explicit target and desired state;
- no bulk or wildcard operation;
- no implicit selection of the current host;
- clear documentation of precedence relative to other router access controls;
- tests for exact action mapping and invalid targets; and
- identified live-router validation.

## Research track: Smart Home REST

The official REST interface is broad enough that automatic client generation
could create a large maintenance burden inconsistent with this fork's doctrine.

Research may document:

- authentication and version requirements;
- overlap with existing `FritzHomeAutomation` behavior;
- one concrete missing user capability; and
- the smallest handwritten wrapper that would solve it.

Do not submit a generated comprehensive REST client as a feature PR. A separate
project may be more appropriate if broad API coverage is the actual goal.

## Research track: internet radio

Internet-radio work remains experimental until the exact request contract is
captured and validated on an identified router and firmware.

An upstream proposal requires all of the following:

- a demonstrated need not met by `call_action()` or a documented API;
- sanitized evidence of the internal request and response contract;
- a clear firmware-compatibility statement;
- no browser-automation dependency in the library;
- no bundled station list;
- no automatic deletion or guessed identifiers; and
- upstream agreement that an undocumented experimental wrapper belongs in the
  project.

The standalone importer may remain a separate tool even when no upstream PR is
appropriate.

## Research track: WireGuard

Before any work, re-check upstream issues and PRs. Do not create competing work
when an active upstream contribution already addresses the need.

Research should focus on testing, protocol evidence, or narrowly requested review
help rather than independently generating another implementation.

## Deferred high-risk capabilities

The following should not be early upstream candidates:

- configuration restore;
- firmware installation;
- factory reset;
- broad SIP-account provisioning;
- bulk call-routing changes;
- bulk voicemail deletion; and
- generic wrappers around undocumented router internals.

These operations have disproportionate safety, testing, and maintenance costs.
They require a specific upstream request and a dedicated design discussion.

## Per-candidate planning record

Before creating a `feature/*` branch, write a short record outside the candidate
branch containing:

```text
Candidate:
Demonstrated user problem:
Existing low-level workaround:
Why a high-level API is still justified:
Upstream issue or discussion:
Confirmed target branch:
Interface class:
Official service or endpoint:
Read-only / mutating / destructive:
Nearest existing module and tests:
Files expected to change:
Explicit exclusions:
New dependency: none / approved exception
Core files changed: normally none
Test plan:
Live-router validation plan:
Maintenance risks:
Stop conditions:
```

If this record cannot be completed confidently, the candidate remains in
`research`.

## PR review budget

There is no rigid line-count limit, but the expected shape is deliberately small:

- one behaviorally coherent production module or enhancement;
- one focused test module plus fixtures;
- one documentation section;
- one to three meaningful commits; and
- no unrelated files.

A diff that exceeds this shape must be divided or explicitly justified before an
upstream PR is opened.

## Immediate next actions

1. Verify that the fork's mirror branches match upstream and determine the current
   development branch used for new features.
2. Prepare a concise upstream issue proposing only Candidate 1.
3. Do not create the feature branch until the issue text and scope receive human
   review.
4. Capture a sanitized, read-only TAM response from the FRITZ!Box 7590 only after
   confirming the required user permissions.
5. Implement Candidate 1 only if the official action and response contracts are
   verified.
6. Run focused tests, full non-router tests, Ruff, mypy, Sphinx, and applicable
   Python-version checks.
7. Review the final diff line by line and open a draft PR only when every claim is
   supportable.

## Success criterion

The roadmap succeeds when upstream receives a small number of contributions that
are easy to understand, safe to review, native to the repository, and affordable
to maintain. Producing fewer PRs is preferable to weakening any of those
qualities.
