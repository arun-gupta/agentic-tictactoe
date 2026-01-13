# Branch Protection Setup Guide

This guide explains how to set up branch protection rules for the `main` branch on GitHub to prevent direct pushes and ensure code quality.

## Why Protect the Main Branch?

Branch protection ensures that:
- All code changes go through pull requests
- Code reviews are required before merging
- CI checks pass before code is merged
- The main branch remains stable and deployable

## Setup Instructions

### Step 1: Navigate to Branch Protection Settings

1. Go to your repository on GitHub
2. Click **Settings** (top navigation bar)
3. Click **Branches** (left sidebar)
4. Under "Branch protection rules", click **Add rule** (or **Add branch protection rule**)

### Step 2: Configure Branch Protection Rule

**Branch name pattern:** `main`

**Recommended Settings:**

#### ✅ Protect matching branches

#### ✅ Require a pull request before merging
- **Required number of approvals:** 1 (or more, depending on your team size)
- ✅ **Dismiss stale pull request approvals when new commits are pushed**
- ✅ **Require review from Code Owners** (optional, if you have a CODEOWNERS file)

#### ✅ Require status checks to pass before merging
- ✅ **Require branches to be up to date before merging**
- Select the following status checks (from your CI workflow):
  - `test / Run formatting check (black)`
  - `test / Run linting (ruff)`
  - `test / Run type checking (mypy)`
  - `test / Run tests with coverage`

#### ✅ Require conversation resolution before merging
- Ensures all PR comments are addressed

#### ✅ Do not allow bypassing the above settings
- Prevents even administrators from bypassing rules (recommended for strict protection)

#### ✅ Restrict who can push to matching branches
- Leave empty (allows PRs to merge) OR
- Add specific users/teams who should never push directly (optional)

#### ✅ Allow force pushes
- ❌ **Uncheck this** (prevents force pushes, which can rewrite history)

#### ✅ Allow deletions
- ❌ **Uncheck this** (prevents accidental branch deletion)

### Step 3: Additional Recommended Settings

#### Lock Branch
- ❌ Uncheck (not necessary for normal development)

#### Allow specified actors to bypass required pull requests
- Optional: Add maintainers if needed (not recommended for strict protection)

## Verification

After setting up branch protection:

1. Try to push directly to `main`:
   ```bash
   git checkout main
   git push origin main
   ```
   This should fail with an error about branch protection.

2. Create a test branch and open a PR:
   ```bash
   git checkout -b test/protection
   git commit --allow-empty -m "test: verify branch protection"
   git push origin test/protection
   ```
   Then open a PR on GitHub - you should see that:
   - PR is required
   - Status checks must pass
   - Reviews are required

## Current CI Status Checks

Based on `.github/workflows/ci.yml`, the following status checks will run:

1. **Run formatting check (black)** - Verifies code formatting
2. **Run linting (ruff)** - Checks code style and linting
3. **Run type checking (mypy)** - Validates type annotations
4. **Run tests with coverage** - Runs test suite and coverage checks

All of these must pass before a PR can be merged (when branch protection is enabled).

## Notes

- Branch protection rules are repository settings, not code files
- Settings apply immediately after configuration
- Existing commits on `main` are not affected
- Branch protection only applies to the specified branch pattern (`main`)
- You can have different rules for different branches (e.g., `main` vs `develop`)

## Troubleshooting

### "Status checks not found"

If status checks don't appear in the list:
1. Ensure CI workflow has run at least once on a PR
2. Wait a few minutes and refresh the branch protection settings page
3. Status checks appear after the workflow runs and reports status

### "Can't merge: required status checks not found"

This means the CI workflow hasn't run yet or hasn't reported status. The status checks will appear after:
1. A PR is created
2. CI workflow runs
3. Status checks report back to GitHub

### Need to merge urgently?

If you need to bypass protection in an emergency:
1. Temporarily disable branch protection (not recommended)
2. Or use the "Allow specified actors to bypass" setting for trusted maintainers
3. Re-enable protection immediately after

## See Also

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Collaboration guidelines
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development workflow
