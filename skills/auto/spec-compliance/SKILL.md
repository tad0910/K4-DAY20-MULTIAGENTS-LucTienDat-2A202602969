---
name: spec-compliance
description: Ensure code follows the exact behavior described in docstrings, including formatting, rounding, and edge cases.
---
- Verify the function signature matches the docstring description.
- Confirm output format (e.g., CSV quoting, decimal places, date/time format) matches the spec.
- Test edge cases mentioned in the docstring (empty strings, negative numbers, special characters).
- Use the docstring examples as unit tests before running the full test suite.
- If the function accepts optional parameters, ensure defaults are documented and used correctly.
- Check that any transformations (e.g., rounding half‑up) follow the rules stated in the docstring.
- Ensure no hidden side‑effects (e.g., modifying global state) unless explicitly documented.
- Validate that error handling messages are consistent with the spec.
- When the docstring specifies a return type, confirm the function returns that type.
- If the function should raise an exception for invalid input, test that the correct exception type and message are used.
