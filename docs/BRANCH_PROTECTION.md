# Branch Protection Setup Guide

This guide explains how to set up branch protection rules for the `main` branch on GitHub to prevent direct pushes and ensure code quality.

## Why Protect the Main Branch?

Branch protection ensures that:
- All code changes go through pull requests
- Code reviews are required before merging
- CI checks pass before code is merged
- The main branch remains stable and deployable

## Setup Instructions

### Step 1: Navigate to Rulesets Settings

1. Go to your repository on GitHub
2. Click **Settings** (top navigation bar)
3. Click **Rules** (left sidebar, under "Code and automation")
4. Click **New ruleset** button (or **Add ruleset**)

### Step 2: Configure Ruleset Name and Target

**Ruleset Name:** `main` (or any descriptive name like "Main Branch Protection")

**Enforcement status:** `Active` (enabled)

**Target branches:**
- Click **Add target** → Select **Default** (this targets the `main` branch)
- Or use **Branch name pattern** to specify `main` explicitly

**Bypass list:** Leave empty (or add specific roles/teams if needed for emergencies)

### Step 3: Configure Branch Rules

#### Restrict deletions
- ✅ **Check** "Restrict deletions" - Only allow users with bypass permission to delete matching refs

#### Require a pull request before merging
- ✅ **Check** "Require a pull request before merging"
- **Required approvals:** Set to `1` (or more, depending on your team size)
- ✅ **Check** "Dismiss stale pull request approvals when new commits are pushed"
- ✅ **Check** "Require review from Code Owners" (if you have a CODEOWNERS file)
- ✅ **Check** "Require conversation resolution before merging"

**Allowed merge methods:** Select `Merge, Squash, Rebase` (or your preferred combination)

### Step 4: Configure Status Checks

#### Require status checks to pass
- ✅ **Check** "Require status checks to pass before the ref is updated"
- ✅ **Check** "Require branches to be up to date before merging"
- ❌ **Uncheck** "Do not require status checks on creation" (unless you want to allow branch creation without checks)

**Add required checks:**
- Click **+ Add checks** button
- Select the following status checks (they will appear after CI runs at least once):
  - `test / Run formatting check (black)`
  - `test / Run linting (ruff)`
  - `test / Run type checking (mypy)`
  - `test / Run tests with coverage`

#### Block force pushes
- ✅ **Check** "Block force pushes" - Prevent users with push access from force pushing to refs

### Step 5: Additional Settings (Optional)

The following are typically left unchecked unless needed:

- ❌ **Restrict creations** - Only allow users with bypass permission to create matching refs
- ❌ **Restrict updates** - Only allow users with bypass permission to update matching refs
- ❌ **Require linear history** - Prevent merge commits from being pushed
- ❌ **Require deployments to succeed** - Require successful deployments before merging
- ❌ **Require signed commits** - Require verified commit signatures
- ❌ **Require code scanning results** - Require code scanning before merging
- ❌ **Require code quality results** - Require code quality analysis before merging

### Step 6: Create the Ruleset

Click the **Create** button at the bottom of the page to save your branch protection ruleset.

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

- Branch protection rulesets are repository settings, not code files
- Settings apply immediately after configuration
- Existing commits on `main` are not affected
- Rulesets can target specific branches or use patterns
- You can create multiple rulesets for different branches (e.g., `main` vs `develop`)
- Rulesets can be edited or deleted from the **Settings → Rules** page

## Troubleshooting

### "Status checks not found" or "No checks have been added"

If status checks don't appear in the list:
1. Ensure CI workflow has run at least once on a PR or push
2. Wait a few minutes and refresh the ruleset settings page
3. Status checks appear after the workflow runs and reports status to GitHub
4. If you see "No checks have been added", click **+ Add checks** and wait for checks to appear, or create a test PR to trigger CI

### "Can't merge: required status checks not found"

This means the CI workflow hasn't run yet or hasn't reported status. The status checks will appear after:
1. A PR is created
2. CI workflow runs
3. Status checks report back to GitHub

### Need to merge urgently?

If you need to bypass protection in an emergency:
1. Temporarily disable the ruleset (Settings → Rules → Edit ruleset → Set enforcement to "Disabled")
2. Or add yourself/team to the "Bypass list" in the ruleset settings
3. Re-enable protection immediately after

## See Also

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Collaboration guidelines
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development workflow
