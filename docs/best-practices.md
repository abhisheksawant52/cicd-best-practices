# CI/CD Best Practices

The rules enforced by `cicd-lint`, and the reasoning behind each.

## 1. Pin actions to a ref (`pinned-actions`, error)

Never reference an action without a version. `actions/checkout` resolves to the
default branch and can change under you; a compromised tag can inject code into
your pipeline. Pin to a released major tag (`actions/checkout@v4`) at minimum, or
a full commit SHA for third-party actions.

## 2. Least-privilege permissions (`least-privilege-permissions`, warning)

The default `GITHUB_TOKEN` may have write scope. Declare a top-level
`permissions:` block and grant only what each job needs:

```yaml
permissions:
  contents: read
```

Escalate per-job (e.g. `packages: write`) only where required.

## 3. Job timeouts (`job-timeouts`, warning)

Set `timeout-minutes` on every job. Without it, a hung step can occupy a runner
for the org default (often 360 minutes), wasting minutes and blocking queues.

## 4. Concurrency control (`concurrency-control`, info)

Use a `concurrency` group to cancel superseded runs on the same ref:

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

## Beyond the linter

- Cache dependencies deterministically (lockfiles + `actions/cache`).
- Separate build, test, and deploy into distinct jobs with explicit `needs`.
- Require status checks and reviews via branch protection.
- Sign artifacts and generate provenance (SLSA) for releases.
