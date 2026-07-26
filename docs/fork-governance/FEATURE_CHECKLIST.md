# Feature Contribution Checklist

Use this checklist for every branch intended to become an upstream PR.

## Scope and discussion

- [ ] The feature solves one clearly stated problem.
- [ ] Existing upstream issues and PRs were searched.
- [ ] A substantial feature has an upstream issue or maintainer discussion.
- [ ] The intended upstream base branch is confirmed.
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

## Repository fit

- [ ] The nearest existing module and tests were reviewed before implementation.
- [ ] The implementation follows `AbstractLibraryBase` and existing `_action()`
      patterns where appropriate.
- [ ] Existing sessions, authentication, exceptions, and helpers are reused.
- [ ] New runtime dependencies were avoided.
- [ ] Core changes are generic and independently justified.
- [ ] The feature does not include unrelated modernization or formatting.
- [ ] Public names and return forms are consistent with neighboring APIs.

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
- [ ] Meaningful machine assistance will be disclosed in the PR.

## Final diff

- [ ] The branch was rebased onto the current upstream base.
- [ ] `git diff --stat upstream/<base>...HEAD` is appropriately small.
- [ ] The full diff contains no unrelated files or changes.
- [ ] The commit log contains one to three understandable commits when practical.
- [ ] Fork-governance documents and experimental artifacts are absent.
- [ ] The PR description states what changed, why, validation performed, and
      known limitations.
- [ ] The PR is opened as a draft until validation is complete.