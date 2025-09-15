# Conventional Commits Guide

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning and changelog generation through semantic-release.

## Commit Message Format

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Types

- **feat**: A new feature (triggers minor version bump)
- **fix**: A bug fix (triggers patch version bump)
- **docs**: Documentation only changes (triggers patch version bump)
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature (triggers patch version bump)
- **perf**: A code change that improves performance (triggers patch version bump)
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to our CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit (triggers patch version bump)

## Breaking Changes

To trigger a major version bump, include `BREAKING CHANGE:` in the footer or add `!` after the type/scope:

```text
feat!: remove deprecated API endpoint

BREAKING CHANGE: The /old-endpoint has been removed. Use /new-endpoint instead.
```

## Examples

### Feature

```text
feat(auth): add JWT token refresh mechanism
```

### Bug Fix

```text
fix(api): handle null values in user profile endpoint
```

### Breaking Change

```text
feat(api)!: restructure user data response format

BREAKING CHANGE: User profile now returns nested objects instead of flat structure
```

### Documentation

```text
docs: update installation instructions in README
```

### Refactoring

```text
refactor(db): optimize database connection pooling
```

## Release Process

1. Make changes and commit using conventional commit format
2. Push to `develop` branch for beta releases
3. Create PR to `main` branch for stable releases
4. Semantic-release will automatically:
   - Analyze commits to determine version bump
   - Generate changelog
   - Create GitHub release
   - Update version in pyproject.toml