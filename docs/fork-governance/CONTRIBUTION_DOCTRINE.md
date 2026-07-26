# Contribution Doctrine

This fork exists to make careful, useful contributions to
`kbr/fritzconnection`. It is not a competing implementation and it is not a
vehicle for rapidly expanding the project through automatically generated code.

## Presumption of minimal change

The default decision is to leave the upstream project unchanged.

A proposed change must demonstrate that it:

1. Solves a specific, stated user or maintainer problem.
2. Adds clear value beyond direct use of the existing low-level API.
3. Fits the project's current architecture and public API conventions.
4. Can be reviewed independently without understanding unrelated work.
5. Does not impose disproportionate long-term maintenance on upstream.
6. Preserves existing behavior unless a separately discussed defect requires a
   change.

Completeness is not a goal by itself. A capability should not be added merely
because FRITZ!OS exposes it or because an agent can generate a wrapper for it.

## Core stability

Treat `fritzconnection/core/` as stable and effectively frozen for normal
feature work.

A feature should first be implemented using the public capabilities already
provided by `FritzConnection`, existing sessions, helpers, and exception types.
A core change is acceptable only when all of the following are true:

- The feature cannot be implemented cleanly without it.
- The need is generic rather than feature-specific.
- The helper is independently understandable and testable.
- Existing behavior and public interfaces remain compatible.
- The core change can be proposed separately before the consuming feature.
- The upstream maintainer has had an opportunity to agree with the direction.

No feature branch may include a speculative core refactor, cleanup, or
modernization.

## Precision over breadth

Work on one small behavior at a time. Prefer a read-only first contribution over
a broad read/write/delete interface. Prefer one documented service action over a
large generated client. Prefer direct, repository-native code over abstraction
introduced for possible future features.

A feature proposal should identify the smallest useful increment and explicitly
list what is out of scope.

## Human authorship and machine assistance

Machine assistance may accelerate research, comparison, test drafting, and
implementation, but it must not determine scope or substitute for engineering
judgment.

Automatically generated code is not considered completed work. Before a change
can be proposed upstream, a human contributor must:

- Understand and be able to explain every changed line.
- Verify protocol and API assumptions against primary documentation or sanitized
  router evidence.
- Remove unnecessary generated abstractions, comments, and defensive code.
- Confirm that the code follows adjacent project patterns rather than a generic
  external style.
- Review the tests for meaningful failure detection.
- Assess backward compatibility, security, privacy, and destructive behavior.
- Decide that the maintenance burden is justified by the user value.

When these conditions cannot be met, the work remains an experiment and must not
be presented as an upstream candidate.

## Sustainable contributions

A contribution is sustainable when:

- It uses a documented interface whenever possible.
- Firmware-specific behavior is localized and explicitly limited.
- It adds no runtime dependency unless upstream has agreed to it.
- It has focused tests for success, failure, missing data, and malformed data as
  appropriate.
- Its documentation states permissions, limitations, compatibility, and risk.
- It does not require knowledge of fork-only tools to maintain.
- It can be removed without disturbing unrelated features.
- Its implementation is smaller and clearer than the maintenance problem it
  creates.

Undocumented interfaces require a higher evidence and maintenance threshold and
should normally remain experimental until more than one firmware or model has
been validated.

## Upstream respect

The upstream maintainer decides whether a capability belongs in the project and
how it should be shaped. An issue or design discussion is not merely a procedural
step; it is the point at which the fork asks whether the work is useful and
consistent with the author's direction.

A declined or deferred proposal is not a reason to merge the feature into the
fork's mirror branches. The research may remain on an `experiment/*` branch or be
maintained as a separate application without changing the identity of
`fritzconnection`.

## Quality gate

An upstream candidate must be rejected or reduced in scope when any of these are
true:

- The diff is difficult to explain in a short technical review.
- The feature depends on guessed fields or unverified behavior.
- The implementation changes core behavior unnecessarily.
- The code introduces a new project-wide pattern.
- The tests mostly reproduce implementation details.
- The feature has no identified user need beyond API completeness.
- The contributor cannot explain every changed line.
- The likely maintenance cost exceeds the demonstrated value.

The desired result is a small number of exceptional contributions, not a large
number of generated ones.
