# Style and Human Review Policy

The fork should extend `fritzconnection` in the style and architecture of the
original project. It should not use feature work as a vehicle to redesign the
repository according to the fork contributors' preferences.

The standard is precision, restraint, and exceptional quality. The objective is
not broad FRITZ!OS coverage or rapid code production. A feature should be added
only when it solves a stated problem and can be maintained in the existing
project without disproportionate burden.

## Project identity

- Keep the original repository, package, author, and maintainer identity intact.
- Preserve existing copyright and author headers.
- Use the existing MIT license for contributed files.
- Credit related issues, PRs, and prior implementations when they informed the
  solution.
- Do not rename the package or describe the fork as a successor project.
- Treat the upstream maintainer's scope and design decisions as authoritative.

## Presumption of minimal change

The preferred implementation is the smallest change that solves the stated
problem.

Before adding code, determine whether the need can already be met through the
existing low-level API, documentation, or a small example. A new high-level
wrapper must provide clear value such as safer behavior, stable parsing, reduced
protocol knowledge for callers, or reusable project-native abstraction.

Do not add a feature merely because FRITZ!OS exposes it. Do not implement a broad
capability family in anticipation of possible future use. Explicitly state what
is out of scope for each candidate.

## Architectural compatibility

New high-level modules should normally:

- Live under `fritzconnection/lib/`.
- Derive from `AbstractLibraryBase`.
- Accept an existing `FritzConnection` instance.
- Use `call_action()` for advertised TR-064 actions.
- Use the existing authenticated HTTP session for HTTP-based interfaces.
- Follow the initialization and `_action()` patterns of adjacent modules.
- Raise existing exception types where they fit.
- Return data in forms consistent with neighboring APIs.

Treat `fritzconnection/core/` as stable and effectively frozen for normal feature
work. Changes to core require a reusable need that cannot be satisfied cleanly in
a feature module. A generic helper should not contain feature-specific
assumptions and should normally be discussed and proposed separately before the
feature that consumes it.

A feature branch must not contain speculative core refactoring, cleanup,
modernization, or behavior changes.

## Deliberate non-modernization

A feature PR should not also:

- Reformat unrelated files.
- Apply `black` or another formatter repository-wide.
- Convert existing APIs to dataclasses, Pydantic, or async programming.
- Replace `setup.py` or reorganize packaging.
- Add broad type annotations outside the public feature API.
- Rename existing public methods for consistency.
- Introduce a new logging, configuration, test, or dependency framework.

A separate modernization proposal may be valid, but it must be discussed and
reviewed independently.

## Public API design

A public method should have one clear responsibility. Prefer explicit methods
over a generic method that requires callers to know undocumented field names.

Read-only, mutating, and destructive actions should be visibly distinct.
Destructive methods must not infer targets or use permissive defaults.

Prefer a read-only first increment when it provides useful value and makes the
feature easier to review. Add mutating or destructive behavior only after the
identifiers, permissions, error cases, and maintenance implications are proven.

For undocumented interfaces:

- Mark the feature experimental in its module and documentation.
- State the tested FRITZ!Box model and FRITZ!OS version.
- Refuse unsafe operations when an identifier or response contract cannot be
  proven.
- Keep firmware-specific parsing localized.
- Avoid presenting an internal endpoint as a stable AVM API.
- Require a stronger user-value case and maintenance plan than for a documented
  interface.

## Sustainability

A contribution should be sustainable without fork-only knowledge or tooling.
Before upstream submission, confirm that it:

- Uses a documented interface whenever possible.
- Adds no runtime dependency unless the maintainer has agreed to it.
- Preserves backward compatibility and unrelated behavior.
- Localizes model- or firmware-specific behavior.
- Documents permissions, limitations, compatibility, and risk.
- Includes focused tests for realistic success and failure conditions.
- Can be removed without changing unrelated features.
- Is smaller and clearer than the maintenance problem it creates.

When probable maintenance cost exceeds demonstrated user value, the work should
remain an experiment or separate application rather than an upstream feature.

## Machine-assisted work

Machine assistance may be used for research, comparison, test drafting, review,
and implementation support. It does not replace human authorship, scope control,
or accountability.

Before a machine-assisted change is offered upstream, the human contributor
must:

1. Understand and be able to explain every changed line.
2. Verify service names, actions, arguments, and response assumptions.
3. Remove generated abstractions that are not needed.
4. Rewrite comments and documentation into direct technical prose.
5. Check that tests assert behavior rather than merely mirror implementation.
6. Review error handling and destructive operations manually.
7. Confirm that no credentials or private router data are present.
8. Run the relevant repository checks.
9. Validate on a real router when the feature depends on model or firmware
   behavior.
10. Assess whether the feature's maintenance burden is justified.
11. Disclose meaningful machine assistance in the PR description.

A generated diff should be treated as an untrusted proposal to reduce and review,
not as completed engineering. Automatically generated breadth is a warning sign,
not evidence of completeness.

## Human-understandable commits

Commits should correspond to technical decisions a reviewer can evaluate.
Examples:

```text
add read-only answering-machine wrapper
parse answering-machine message list
add tests for voicemail state parsing
document FritzTAM read operations
```

Avoid development-history commits such as:

```text
work in progress
try again
AI fixes
misc cleanup
format everything
```

Before upstream submission, interactive rebase may be used to combine noisy
local commits into one to three meaningful commits without concealing distinct
reviewable concerns.

## Review questions

Every candidate should be reviewed against these questions:

- Does this solve one stated problem?
- Is the change the minimum useful increment?
- Does the code look native to this repository?
- Could the need be met without adding a new public API?
- Is a core change truly necessary, generic, and separately reviewable?
- Is the interface documented or explicitly experimental?
- Can the feature be removed without affecting unrelated behavior?
- Are mutating and destructive operations safe and explicit?
- Do tests cover failure paths and malformed responses?
- Is live-router evidence identified without exposing private data?
- Is the diff free from unrelated cleanup?
- Is the maintenance burden proportionate to the demonstrated value?
- Can the contributor explain the design without relying on generated text?

If any answer is unclear, reduce the scope or keep the work experimental.
