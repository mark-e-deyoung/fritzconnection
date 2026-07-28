# TAM Upstream Handoff

Status date: 2026-07-28

## Current state

The fork contains a validated, stacked answering-machine implementation:

- `feature/tam-read-only` — draft PR #1
- `feature/tam-message-state` — draft PR #2
- `feature/tam-enable` — draft PR #3
- `feature/tam-delete-message` — draft PR #4
- `integration/tam-local-test` — combined local validation branch

All four fork PRs are open, remain drafts, and were mergeable at the last check.
`master` matches `kbr/fritzconnection:master`.

Live validation on a FRITZ!Box 7590 running FRITZ!OS 8.x completed successfully for:

- read-only TAM discovery and information;
- voicemail message-list retrieval and parsing;
- one message read-state toggle, verification, and restoration; and
- one TAM enable-state toggle, verification, and restoration.

Voicemail deletion was not live-tested and remains optional and deferred.

The sanitized validation summary is on `integration/tam-local-test` at:

`docs/testing/fritztam-validation-summary.md`

## Upstream coordination point

Upstream already has an older overlapping contribution:

- `kbr/fritzconnection` PR #140, `new library module fritztam`
- https://github.com/kbr/fritzconnection/pull/140

The older PR remains open but is not mergeable in its present form. Its original
contributor later stated that they had lost interest and invited another
contributor to prepare a new PR.

Relevant maintainer feedback on that PR included:

- prefer a non-abbreviated public name such as `FritzAnsweringMachine`;
- follow PEP 8 naming; and
- avoid variable names that encode container types.

## Alignment comment status

A maintainer-alignment comment has been prepared, but it was **not posted** as of
the status date. The connected GitHub integration can read upstream PR #140 but
received HTTP 403 when attempting to comment.

The first action before waiting for a reply is therefore to post the prepared
comment manually using an authenticated GitHub session. The comment should ask:

1. whether a clean successor PR containing only the read-only capability is
   welcome;
2. which upstream branch it should target; and
3. whether `FritzAnsweringMachine` is still preferred over `FritzTAM`.

The initial upstream proposal must remain limited to:

- `GetInfo`;
- `GetList`;
- `GetMessageList` and message metadata parsing;
- focused tests and documentation;
- no core changes;
- no runtime dependencies; and
- no CLI.

Do not mention or submit the mutation branches as part of the initial proposal,
except to state that no additional behavior will be proposed without separate
maintainer interest.

## Resume procedure after a maintainer reply

1. Read the complete new reply and the surrounding PR #140 discussion.
2. Record the confirmed target branch and naming direction in this file or the
   focused PR roadmap.
3. Do not modify `master`.
4. Create a new clean successor branch directly from the maintainer-selected
   upstream branch.
5. Transfer only the read-only implementation from fork PR #1.
6. Apply the requested class/module naming before opening an upstream PR.
7. Re-run focused tests, repository checks, mypy, documentation, build, and
   sanitized live read-only validation as applicable.
8. Open one draft upstream PR that references PR #140 and credits the earlier
   contributor.
9. Keep fork PRs #2–#4 deferred until PR #1 is accepted, declined, or receives
   explicit follow-on direction.

## Decision handling

- **Positive, branch and naming confirmed:** prepare the clean successor branch.
- **Positive but ambiguous:** ask one concise follow-up question before coding.
- **Requests changes to API shape:** revise only the read-only design in the fork
  and revalidate before submission.
- **No interest or explicit rejection:** retain the implementation in the fork;
  do not submit the mutation branches upstream.
- **No reply:** do not treat silence as approval. Keep all fork PRs as drafts and
  avoid starting another TAM upstream submission.

## Known fork references

- Fork PR #1: https://github.com/mark-e-deyoung/fritzconnection/pull/1
- Fork PR #2: https://github.com/mark-e-deyoung/fritzconnection/pull/2
- Fork PR #3: https://github.com/mark-e-deyoung/fritzconnection/pull/3
- Fork PR #4: https://github.com/mark-e-deyoung/fritzconnection/pull/4
- Governance roadmap: `docs/fork-governance/PR_ROADMAP.md`

## Stop conditions

Stop and reassess before submission if the maintainer requests a core change, a
new runtime dependency, a broad feature bundle, an undocumented interface, or a
branch target that cannot be reproduced cleanly from upstream history.
