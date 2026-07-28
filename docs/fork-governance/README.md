# Fork Governance

This fork is a contribution workspace for `kbr/fritzconnection`.

The purpose of the fork is to research, implement, validate, and offer narrowly
scoped improvements back to the original project. It is not intended to replace,
rename, or subsume the upstream project.

The fork values precision over breadth. The desired outcome is a small number of
exceptional, sustainable contributions rather than a large body of automatically
generated code.

## Governing principles

1. Preserve the upstream author's architecture, style, and project identity.
2. Treat no change as the default; require a specific, demonstrated need.
3. Keep upstream mirror branches free of fork-only changes.
4. Develop one understandable capability at a time.
5. Separate protocol research from code proposed for upstream inclusion.
6. Open or reference an upstream issue before investing in a substantial PR.
7. Require human review and ownership of all machine-assisted contributions.
8. Prefer documented FRITZ!Box interfaces over firmware-specific internal APIs.
9. Clearly label experimental features that rely on undocumented interfaces.
10. Validate behavior with unit tests and, where needed, an identified router and
    FRITZ!OS version.
11. Treat `fritzconnection/core/` as stable and avoid changing it for normal
    feature work.
12. Make every upstream candidate independently reviewable, removable, and
    proportionate to its maintenance burden.

Completeness of FRITZ!OS coverage is not itself a reason to add a feature. Each
candidate must solve a stated problem and fit the upstream maintainer's direction.

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
A feature branch must not contain speculative core refactoring, cleanup, or
modernization.

## Fork-only material

Fork governance, capability matrices, sanitized captures, local runbooks,
validation notes, and experimental tooling belong on `meta/*` or
`experiment/*` branches. They must not be merged into upstream mirror branches
or included accidentally in upstream PRs.

## Related documents

- [Contribution doctrine](CONTRIBUTION_DOCTRINE.md)
- [Focused upstream PR roadmap](PR_ROADMAP.md)
- [TAM upstream handoff](TAM-UPSTREAM-HANDOFF.md)
- [Upstream contribution workflow](UPSTREAM_WORKFLOW.md)
- [Style and human review policy](STYLE_AND_REVIEW.md)
- [Feature contribution checklist](FEATURE_CHECKLIST.md)
- [Local agent prompt package](../../prompts/fork-contribution-workflow.md)

The upstream project's own `CONTRIBUTING.md` remains authoritative for any PR
submitted to `kbr/fritzconnection`.
