# Documentation Index

All persistent project documentation lives under this directory.

## CI / CD Pipeline

Two workflows cover all changes:

- **Pull Request Gate** — `.github/workflows/pr_gate.yml` runs on every PR targeting `main`. It validates the PR head (lint, type-check, tests) and cancels in-progress runs when a new commit lands on the PR.
- **Release Pipeline** — `.github/workflows/release.yml` runs on every push to `main` and via `workflow_dispatch`. It re-validates the exact commit being released, computes a CalVer tag (`YYYY.MM.DD` or `YYYY.MM.DD.Micro`), creates and pushes the tag, builds any artifacts, and creates a GitHub Release with those artifacts attached.

Tags are **CalVer only**. Legacy non-CalVer tags have been cleaned up.

## Documentation Conventions

When behavior, API contracts, deployment steps, or architecture change, update the relevant doc under this `docs/` tree in the same change. Code and docs must stay in sync.

For authoritative rules on verification, review, conventions, and context efficiency, see [openspec/config.yaml](../openspec/config.yaml) (when present in this repo).
