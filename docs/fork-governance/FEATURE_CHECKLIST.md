# Feature Contribution Checklist

Use this checklist for every branch intended to become an upstream PR.

## Need and scope

- [ ] The feature solves one clearly stated user or maintainer problem.
- [ ] The feature is not being added merely for FRITZ!OS API completeness.
- [ ] Existing upstream issues and PRs were searched.
- [ ] A substantial feature has an upstream issue or maintainer discussion.
- [ ] The intended upstream base branch is confirmed.
- [ ] The smallest useful increment is identified.
- [ ] Out-of-scope behavior is stated explicitly.
- [ ] Existing low-level APIs, documentation, or an example cannot satisfy the
      need adequately without a new public wrapper.
- [ ] The work is not better divided into a low-level helper PR and a separate
      consumer PR.

## Branch integrity

- [ ] The branch name uses `feature/<narrow-capability>`.
- [ ] The branch started directly from the confirmed upstream base.
- [ ] The branch does not contain commits from `meta/*`, `experiment/*`, or
      `integration/*`.
- [ ] Upstream mirror branches remain untouched by fork-only work.
- [ ] The final branch contains no merge commits from integration branches.

## Interface evidence

- [ ] The interface is classified as TR-064, AHA, REST, or undocumented HTTP/Lua.
- [ ] Service names, actions, paths, and arguments are recorded.
- [ ] Required FRITZ!Box user permissions are documented.
- [ ] Read-only, mutating, and destructive operations are identified.
- [ ] Router model and FRITZ!OS version are recorded where relevant.
- [ ] Undocumented behavior is clearly labeled experimental.
- [ ] No production behavior depends on guessed fields or identifiers.

## Repository fit

- [ ] The nearest existing module and tests were reviewed before implementation.
- [ ] The implementation follows `AbstractLibraryBase` and existing `_action()`
      patterns where appropriate.
- [ ] Existing sessions, authentication, exceptions, and helpers are reused.
- [ ] New runtime dependencies were avoided.
- [ ] `fritzconnection/core/` is unchanged unless a separately justified generic
      need was agreed with upstream.
- [ ] Any core change is independently understandable, backward compatible, and
      free of feature-specific assumptions.
- [ ] The feature does not include unrelated modernization or formatting.
- [ ] Public names and return forms are consistent with neighboring APIs.
- [ ] The implementation introduces no new project-wide pattern.

## Sustainability

- [ ] The demonstrated user value justifies the likely maintenance burden.
- [ ] A documented interface is used whenever possible.
- [ ] Firmware- or model-specific behavior is localized.
- [ ] The feature can be removed without affecting unrelated behavior.
- [ ] The feature does not require fork-only tools or knowledge to maintain.
- [ ] Compatibility, permissions, limitations, and risk are documented.
- [ ] The implementation is smaller and clearer than the maintenance problem it
      creates.
- [ ] Broad generated coverage was reduced to the minimum useful behavior.

## Safety and privacy

- [ ] Destructive operations require an explicit target.
- [ ] No unsafe default can delete or overwrite unknown data.
- [ ] Ambiguous identifiers cause a refusal rather than a guessed action.
- [ ] Fixtures and captures are sanitized.
- [ ] No credentials, session IDs, serial numbers, telephone numbers, contact
      data, MAC addresses, or public IP addresses are committed.

## Tests and documentation

- [ ] Unit tests cover successful behavior.
- [ ] Tests cover authorization, malformed responses, and missing data where
      relevant.
- [ ] Tests would fail for a real behavioral defect rather than merely mirror the
      implementation.
- [ ] Parsers use sanitized fixtures when realistic payloads matter.
- [ ] Model- or firmware-dependent behavior has an opt-in `routertest` or a
      manual validation record.
- [ ] Public classes, methods, arguments, return values, and limitations are
      documented.
- [ ] The documentation distinguishes official from undocumented interfaces.

## Required checks

- [ ] Focused tests pass.
- [ ] Non-router test suite passes.
- [ ] Ruff passes.
- [ ] Mypy passes for the applicable repository scope.
- [ ] Sphinx documentation builds.
- [ ] Supported Python-version tests pass or any limitation is explained.
- [ ] Router tests were run when necessary and the test environment is recorded.

## Human review

- [ ] The human contributor understands every changed line.
- [ ] Machine-generated abstractions and unnecessary comments were removed.
- [ ] The contributor independently verified protocol and API assumptions.
- [ ] Tests were reviewed for meaningful assertions.
- [ ] Error handling and destructive behavior were manually reviewed.
- [ ] Backward compatibility and core non-interference were reviewed.
- [ ] The contributor accepts the long-term maintenance implications.
- [ ] Meaningful machine assistance will be disclosed in the PR.

## Final diff

- [ ] The branch was rebased onto the current upstream base.
- [ ] `git diff --stat upstream/<base>...HEAD` is appropriately small.
- [ ] The full diff contains no unrelated files or changes.
- [ ] The commit log contains one to three understandable commits when practical.
- [ ] Fork-governance documents and experimental artifacts are absent.
- [ ] The PR description states what changed, why, validation performed, known
      limitations, and explicit out-of-scope behavior.
- [ ] The PR explains why the public API and maintenance burden are justified.
- [ ] The PR is opened as a draft until validation is complete.

A candidate that cannot satisfy these checks should be reduced, retained as an
experiment, or maintained as a separate application rather than offered upstream.
