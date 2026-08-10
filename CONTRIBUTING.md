# Contributing to ownjoo/utils

Thank you for contributing to ownjoo/utils! This document provides guidelines for making contributions to this shared utilities library.

## Standards & Philosophy

This repository follows the ownjoo standards and principles defined in [CLAUDE.md](https://github.com/ownjoo/claude/blob/main/CLAUDE.md).

**Key principles:**

- **Simplicity First** — Write the simplest code that solves the problem. No premature optimization or over-engineering.
- **Pragmatic Testing** — Use mocks in unit tests where appropriate, and integration tests that hit real dependencies when needed.
- **Explicit Commits** — Use conventional commits (feat/fix/refactor/docs/test/chore).
- **No Defensive Code** — Don't add error handling for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries.
- **Documentation as Code** — Keep documentation close to implementation. Update docs in the same PR as code changes.
- **Security by Default** — Never introduce OWASP Top 10 vulnerabilities. Review code for these before committing.

## Before You Start

1. **Read CLAUDE.md** — Understand the organization-wide standards at https://github.com/ownjoo/claude/blob/main/CLAUDE.md
2. **Check Existing Issues** — Your idea might already be discussed or planned
3. **Open an Issue First** — For feature requests, discuss the approach before implementing

## Development Workflow

### 1. Setup Your Environment

```bash
git clone https://github.com/ownjoo/ownjoo-toolkit.git
cd ownjoo-toolkit
pip install -e ".[dev]"
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b bugfix/your-bug-name
# or for refactoring:
git checkout -b refactor/your-refactor-name
```

### 3. Make Your Changes

- **Keep commits small and focused** — One logical change per commit
- **Use conventional commit format** — See [Commit Messages](#commit-messages) below
- **Add tests alongside your code** — Tests go in the same PR as code changes
- **Update documentation** — If you change public APIs, update README.md and docstrings

### 4. Test Your Changes

```bash
# Run all tests
python -m pytest test/ -v

# Run with coverage
python -m pytest test/ --cov=oj_toolkit --cov-report=html

# Check code style
black --check oj_toolkit/
ruff check oj_toolkit/
```

### 5. Format Your Code

```bash
black oj_toolkit/
```

### 6. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a PR on GitHub. Include:
- Clear title (under 70 characters)
- Description of what changed and why
- Testing approach
- Link to related issues

## Code Standards

### Python Version
- **Minimum:** Python 3.11+
- Use type hints throughout

### Imports
- Remove unused imports
- Delete dead code entirely (don't use `_` prefixes)
- Use relative imports within the package

### Docstrings
- Add docstrings to all public functions and modules
- Include parameter descriptions, return types, and usage examples
- Document edge cases and error handling
- Use Google-style docstrings (see examples in parsing/types.py)

### Comments
- Only add comments where logic isn't self-evident
- Don't add re-export comments or "removed" markers
- Code should be self-documenting

### Type Hints
- Use type hints for all function parameters and return types
- Use `Optional[Type]` for nullable values, not `Type | None`
- Use `Union[Type1, Type2]` for multiple types

### Functions & Utilities
- Keep functions focused and simple
- Don't create utilities for one-time operations
- Three similar lines of code is better than a premature abstraction
- Use existing utilities from this library (don't duplicate)

## Testing

### Requirements
- **Coverage:** Aim for >80% coverage on new code
- **Test Framework:** Use pytest
- **Test Location:** `test/unit/<module>/` (mirror the package structure)
- **Test Files:** Name as `test_<functionality>.py`

### Test Structure

```python
import unittest
from module import function_to_test

class TestFunctionality(unittest.TestCase):
    def test_should_do_something(self):
        # setup
        expected = 'value'
        
        # execute
        actual = function_to_test('input')
        
        # assess
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
```

### Testing Patterns

- **Unit tests** — Test functions in isolation with mocked dependencies
- **Integration tests** — Test with real dependencies when appropriate (e.g., actual datetime parsing)
- **Edge cases** — Test None, empty inputs, boundary conditions
- **Error paths** — Test that exceptions are logged and handled appropriately

See `test/unit/parsing/test_parsing.py` for good examples.

## Commit Messages

Use **conventional commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:** One of feat, fix, refactor, docs, test, chore

**Scope:** The module affected (e.g., parsing, logging, asynchronous)

**Subject:** Present tense, imperative, lowercase, no period. Max 50 chars.

**Body:** Explain what and why (not how). Wrap at 72 chars. Optional.

**Footer:** Issue references. Optional.

**Example:**

```
feat(parsing): add format_str parameter to get_datetime

Allow custom datetime format strings via format_str parameter. This
enables parsing of non-standard datetime formats that don't match
the predefined TimeFormats enum.

Closes #42
```

**Important:** Always include the Co-Authored-By trailer:

```
Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

## Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows the style guide (black, ruff checks pass)
- [ ] All tests pass (`pytest test/ -v`)
- [ ] Coverage >80% for new code
- [ ] Docstrings added to public functions/modules
- [ ] README.md updated with examples (if public API change)
- [ ] Commit messages follow conventional commit format
- [ ] No security vulnerabilities (OWASP Top 10 review)
- [ ] No debug code or commented-out lines left behind

## Security

**Never:**
- Commit secrets, API keys, or credentials to git
- Introduce command injection vulnerabilities
- Introduce SQL injection vulnerabilities
- Introduce XSS vulnerabilities
- Introduce arbitrary code execution paths

**Always:**
- Validate input at system boundaries (user input, external APIs)
- Use parameterized queries and safe APIs
- Review code for OWASP Top 10 issues before committing
- Use `.gitignore` for local secrets (use `.env.local`, not `.env`)

## Review Process

1. **CI Checks** — All GitHub Actions must pass
2. **Code Review** — At least one maintainer must review and approve
3. **Coverage** — New code must have >80% test coverage
4. **Security Scanning** — Any security issues must be resolved

Maintainers will provide feedback on:
- Code clarity and simplicity
- Test coverage
- Documentation completeness
- Compliance with CLAUDE.md standards
- Security concerns

## Versioning

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backward-compatible functionality
- **PATCH** version for backward-compatible bug fixes

Any public API change must include thorough documentation and examples.

## Questions?

- **Issues:** Use GitHub issues for bugs and feature requests
- **Discussions:** Use GitHub discussions for questions and ideas
- **Standards:** Refer to [CLAUDE.md](https://github.com/ownjoo/claude/blob/main/CLAUDE.md) for organization-wide guidelines

## License

By contributing to ownjoo/utils, you agree that your contributions will be licensed under the same license as this project.
