# Codecov Setup Guide

## Overview

Codecov is already configured in `.github/workflows/ci.yml` to upload coverage data. This guide explains how to set it up and use it to track historical coverage data.

## Quick Setup (Free for Public Repos)

1. **No setup required!** Codecov works automatically for public repositories.

2. **Enable Codecov for your repository:**
   - Go to https://codecov.io
   - Sign in with GitHub
   - Add your repository: `arun-gupta/agentic-tictactoe`
   - Codecov will automatically start receiving coverage data from GitHub Actions

## What Codecov Provides

### 1. **Coverage Dashboard**
   - Web dashboard at: `https://codecov.io/gh/arun-gupta/agentic-tictactoe`
   - Historical coverage graphs
   - File-by-file coverage breakdown
   - Coverage trends over time

### 2. **GitHub PR Comments**
   - Automatic comments on pull requests showing:
     - Coverage change (diff)
     - Coverage percentage
     - Files changed with coverage
     - Coverage graph

### 3. **Coverage Badge**
   - Add to README.md:
     ```markdown
     [![codecov](https://codecov.io/gh/arun-gupta/agentic-tictactoe/branch/main/graph/badge.svg)](https://codecov.io/gh/arun-gupta/agentic-tictactoe)
     ```
   - Shows current coverage percentage
   - Links to coverage dashboard

### 4. **Status Checks**
   - Coverage status checks in GitHub PRs
   - Can be configured to require coverage thresholds
   - Shows if coverage increased/decreased

## Configuration

### Current Setup

The CI workflow (`.github/workflows/ci.yml`) already:
- Runs tests with coverage: `pytest tests/ -v --cov=src --cov-report=xml --cov-report=term`
- Generates `coverage.xml` file
- Uploads to Codecov using `codecov/codecov-action@v4`

### Codecov Configuration File

A `codecov.yml` file has been created with:
- Coverage target: 80%
- Coverage threshold: 1% (fail if coverage drops by 1%)
- Patch coverage: 80% (coverage for changed code in PRs)
- Comment layout for PR comments
- Files to ignore (tests/, __pycache__, etc.)

## Tracking Coverage Over Time

### View Coverage Trends

1. **In Codecov Dashboard:**
   - Visit: `https://codecov.io/gh/arun-gupta/agentic-tictactoe`
   - Click on "Graphs" or "Analytics"
   - See coverage trends over commits/branches

2. **In GitHub:**
   - PR comments show coverage diff
   - Coverage badge in README shows current coverage
   - Codecov status check shows pass/fail

### Coverage Reports

- **Total Coverage**: Overall percentage of code covered
- **File Coverage**: Coverage for each file
- **Diff Coverage**: Coverage for code changed in PR
- **Branch Coverage**: Coverage by git branch

## Best Practices

1. **Keep coverage high**: Aim for 80%+ coverage
2. **Monitor trends**: Watch for coverage drops
3. **Use PR comments**: Review coverage changes in each PR
4. **Set thresholds**: Use `codecov.yml` to enforce minimum coverage
5. **Flag coverage**: Use flags to track different test types (unit, integration, e2e)

## Advanced Features

### Flags (for different test types)

When you have multiple test suites, use flags:

```yaml
- name: Run unit tests with coverage
  run: pytest tests/unit/ --cov=src --cov-report=xml --cov-report=term-missing

- name: Run integration tests with coverage
  run: pytest tests/integration/ --cov=src --cov-report=xml --cov-report=term-missing

- name: Upload coverage (unit tests)
  uses: codecov/codecov-action@v4
  with:
    files: ./coverage.xml
    flags: unit
    name: unit-tests

- name: Upload coverage (integration tests)
  uses: codecov/codecov-action@v4
  with:
    files: ./coverage.xml
    flags: integration
    name: integration-tests
```

### Coverage Status Checks

Configure in `codecov.yml`:
- `target`: Minimum coverage percentage
- `threshold`: Maximum allowed coverage drop
- `base`: Comparison base (auto, parent, commit, etc.)

## Troubleshooting

1. **No coverage data showing:**
   - Check GitHub Actions logs for upload step
   - Verify `coverage.xml` is being generated
   - Check Codecov dashboard for upload status

2. **Coverage not updating:**
   - Ensure workflow runs on pushes/PRs
   - Check if `if: always()` condition is present
   - Verify Codecov has access to repository

3. **Badge not showing:**
   - Wait a few minutes after first upload
   - Check badge URL matches repository name
   - Verify repository is public (or token is configured)

## Next Steps

1. Push code to trigger first coverage upload
2. Visit Codecov dashboard to see data
3. Add coverage badge to README.md
4. Review coverage in PRs
5. Monitor coverage trends over time
