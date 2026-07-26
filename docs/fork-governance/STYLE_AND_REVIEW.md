# Style and Human Review Policy

The fork should extend `fritzconnection` in the style and architecture of the
original project. It should not use feature work as a vehicle to redesign the
repository according to the fork contributors' preferences.

## Project identity

- Keep the original repository, package, author, and maintainer identity intact.
- Preserve existing copyright and author headers.
- Use the existing MIT license for contributed files.
- Credit related issues, PRs, and prior implementations when they informed the
  solution.
- Do not rename the package or describe the fork as a successor project.

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

Changes to `fritzconnection/core/` require a reusable need that cannot be
satisfied cleanly in a feature module. A generic helper should not contain
feature-specific assumptions.

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

For undocumented interfaces:

- Mark the feature experimental in its module and documentation.
- State the tested FRITZ!Box model and FRITZ!OS version.
- Refuse unsafe operations when an identifier or response contract cannot be
  proven.
- Keep firmware-specific parsing localized.
- Avoid presenting an internal endpoint as a stable AVM API.

## Machine-assisted work

Machine assistance may be used for research, comparison, test generation,
review, and implementation support. It does not replace human authorship or
accountability.

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
10. Disclose meaningful machine assistance in the PR description.

A generated diff should be treated as a proposal to review, not as completed
engineering.

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
- Does the code look native to this repository?
- Is a core change truly generic?
- Is the interface documented or explicitly experimental?
- Can the feature be removed without affecting unrelated behavior?
- Are mutating and destructive operations safe and explicit?
- Do tests cover failure paths and malformed responses?
- Is live-router evidence identified without exposing private data?
- Is the diff free from unrelated cleanup?
- Can the contributor explain the design without relying on generated text?