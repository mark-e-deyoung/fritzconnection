# Upstream Contribution Workflow

This workflow keeps development in the fork while producing small changes that
can be reviewed and accepted independently by `kbr/fritzconnection`.

## 1. Synchronize the mirrors

Configure the original repository as `upstream` in a local clone:

```bash
git remote add upstream https://github.com/kbr/fritzconnection.git
git fetch upstream --prune
```

Update mirror branches only by fast-forwarding:

```bash
git switch master
git merge --ff-only upstream/master
git push origin master
```

When upstream has a `v2-development` branch:

```bash
git switch v2-development
git merge --ff-only upstream/v2-development
git push origin v2-development
```

Do not merge feature, experiment, integration, or meta branches into an upstream
mirror branch.

## 2. Classify the proposed work

Record the interface and risk category before coding:

- Documented TR-064
- Documented AHA HTTP
- Documented REST/OpenAPI
- Undocumented SID-authenticated HTTP or Lua

Also record:

- FRITZ!Box model
- FRITZ!OS version
- Service and actions or HTTP endpoints
- Required user permissions
- Whether the operation is read-only, mutating, or destructive
- Whether the behavior has been verified on a real router

Undocumented endpoints must be treated as experimental until the maintainer
accepts the proposed compatibility policy.

## 3. Discuss substantial work first

Before writing a large feature:

1. Search upstream issues and PRs for prior work.
2. Open an upstream issue describing the user need and proposed shape.
3. Ask which branch the maintainer wants the work based on.
4. Ask whether a low-level helper and its consumer should be separate PRs.
5. Do not assume that fork architecture decisions belong upstream.

A small bug fix may not require a new issue, but feature work normally should.

## 4. Create an isolated feature branch

Start directly from the confirmed upstream base:

```bash
git fetch upstream --prune
git switch --create feature/tam-message-list upstream/v2-development
```

The branch name should identify one capability, not a broad program of work.
Avoid branches such as `feature/telephony-overhaul` or
`feature/fritzos-automation`.

## 5. Follow existing repository patterns

Prefer the smallest change that fits the current codebase:

- Derive high-level modules from `AbstractLibraryBase`.
- Reuse `FritzConnection.call_action()` for TR-064 services.
- Reuse the existing authenticated session for HTTP operations.
- Use a small `_action()` method when consistent with neighboring modules.
- Preserve dictionary-oriented APIs unless a new object is clearly justified.
- Avoid new runtime dependencies.
- Avoid repository-wide typing, formatting, or packaging changes.
- Keep core changes separate when they are independently reusable.

Read the neighboring module and its tests before implementing a new one.

## 6. Validate in layers

Use four levels of evidence:

1. Pure unit tests with mocks or controlled responses.
2. Parser tests with sanitized fixtures.
3. Opt-in tests marked `routertest` for a real FRITZ!Box.
4. A manual checklist for mutating or destructive behavior.

Typical checks for a focused feature are:

```bash
nox -s test -- fritzconnection/tests/test_<feature>.py
nox -s check
nox -s mypy
nox -s sphinx
nox -s test_versions -- fritzconnection/tests/test_<feature>.py
```

Router tests remain opt-in:

```bash
nox -s test_router
```

Never commit credentials, session IDs, telephone numbers, contact data, router
serial numbers, MAC addresses, public IP addresses, or unredacted captures.

## 7. Prepare the candidate for human review

Before opening a PR:

```bash
git fetch upstream --prune
git rebase upstream/<confirmed-base>
git diff --stat upstream/<confirmed-base>...HEAD
git diff upstream/<confirmed-base>...HEAD
git log --oneline upstream/<confirmed-base>..HEAD
```

The candidate should have:

- A single stated purpose
- Focused implementation and tests
- Documentation for public behavior
- No fork-governance files
- No experimental captures
- No unrelated cleanup
- No merge commits from integration branches
- A short, understandable commit history

## 8. Open the upstream PR

The PR description should explain:

- What user or developer problem is solved
- Which documented service or observed endpoint is used
- Why the design follows existing project patterns
- What was tested and on which router/firmware, when applicable
- What remains unsupported
- Whether machine assistance was used and how the human contributor reviewed it

Open as a draft until router validation and all requested checks are complete.
Allow upstream maintainers to modify the branch when appropriate.

## 9. After upstream review

Respond to review comments with targeted commits. Do not use review feedback as
an opportunity for unrelated refactoring.

After a PR is merged or declined:

- Preserve protocol research on an `experiment/*` branch or issue.
- Delete stale feature branches when their history is no longer needed.
- Fast-forward the fork's mirror branch from upstream.
- Do not carry a merged feature as a fork-only patch.