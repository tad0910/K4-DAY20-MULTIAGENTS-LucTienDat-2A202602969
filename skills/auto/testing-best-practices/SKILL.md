---
name: testing-best-practices
description: Add comprehensive tests, type hints, and changelog entries to maintain code quality and traceability.
---
- Add type annotations for all public functions (parameters and return values).
- Create a `tests/test_regressions.py` with one test per bug fixed; ensure it passes.
- Update `CHANGELOG.md` under `## Unreleased` with a bullet for each fix: `- fix(<function>): <short description>`.
- Do not modify existing test files; only add new ones.
- Ensure tests cover edge cases, docstring examples, and error conditions.
- Run the full test suite locally before committing to catch hidden failures.
- Verify that the test runner reports 100% coverage for the modified modules.
- Use `pytest` fixtures for setup/teardown to keep tests isolated.
- Keep test names descriptive and follow the `test_<function>_<scenario>` pattern.
- Document any new helper functions used in tests in a `tests/__init__.py` if necessary.
