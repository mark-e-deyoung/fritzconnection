# Fork Governance

This fork is a contribution workspace for `kbr/fritzconnection`.

The purpose of the fork is to research, implement, validate, and offer narrowly
scoped improvements back to the original project. It is not intended to replace,
rename, or subsume the upstream project.

## Governing principles

1. Preserve the upstream author's architecture, style, and project identity.
2. Keep upstream mirror branches free of fork-only changes.
3. Develop one understandable capability at a time.
4. Separate protocol research from code proposed for upstream inclusion.
5. Open or reference an upstream issue before investing in a substantial PR.
6. Require human review and ownership of all machine-assisted contributions.
7. Prefer documented FRITZ!Box interfaces over firmware-specific internal APIs.
8. Clearly label experimental features that rely on undocumented interfaces.
9. Validate behavior with unit tests and, where needed, an identified router and
   FRITZ!OS version.
10. Make every upstream candidate independently reviewable and removable.

## Branch model

The fork uses four branch classes:

| Branch pattern | Purpose | Upstream PR candidate |
| --- | --- | --- |
| `feature/*` | One narrowly scoped contribution | Yes |
| `experiment/*` | Protocol discovery and prototypes | No |
| `integration/*` | Combined testing of several features | No |
| `meta/*` | Fork governance and workbench material | No |

The following branches are treated as upstream mirrors:

- `master` mirrors `kbr/fritzconnection:master`.
- `v2-development` mirrors `kbr/fritzconnection:v2-development` when present.

No fork-specific work should be committed directly to an upstream mirror branch.

## Feature-branch rule

Every `feature/*` branch must begin directly from the upstream branch that the
prospective PR will target. A feature branch must not be based on an
`experiment/*`, `integration/*`, or `meta/*` branch.

A typical upstream candidate should change only files such as:

```text
fritzconnection/lib/<feature>.py
fritzconnection/tests/test_<feature>.py
docs/sources/library_modules.rst
```

Changes to `fritzconnection/core/` require an explicit, reusable need and should
normally be proposed separately from the high-level feature that consumes them.

## Fork-only material

Fork governance, capability matrices, sanitized captures, local runbooks,
validation notes, and experimental tooling belong on `meta/*` or
`experiment/*` branches. They must not be merged into upstream mirror branches
or included accidentally in upstream PRs.

## Related documents

- [Upstream contribution workflow](UPSTREAM_WORKFLOW.md)
- [Style and human review policy](STYLE_AND_REVIEW.md)
- [Feature contribution checklist](FEATURE_CHECKLIST.md)
- [Local agent prompt package](../../prompts/fork-contribution-workflow.md)

The upstream project's own `CONTRIBUTING.md` remains authoritative for any PR
submitted to `kbr/fritzconnection`.