# PR Order for Re-opened Changes

This repository currently contains two key commits after `Initial commit`:

1. `f97b83b` — Core AI News Publisher implementation (backend, frontend scaffold, tests, docs).
2. `5c9feb0` — Frontend follow-up fixes for missing `frontend/lib/*` modules and safer API sorting.

When recreating closed PRs, open them in this order:

## PR 1 (base)
- Include: commit `f97b83b`
- Title suggestion: `Implement AI News Publisher core platform (backend, frontend, tests)`

## PR 2 (follow-up)
- Include: commit `5c9feb0`
- Base: PR 1 branch (or main after PR 1 merge)
- Title suggestion: `Fix Next.js frontend data layer and lib tracking`

This preserves reviewability and matches the order the changes were authored.
