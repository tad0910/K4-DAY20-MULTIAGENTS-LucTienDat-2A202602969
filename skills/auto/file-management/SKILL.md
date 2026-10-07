---
name: file-management
description: Handle file I/O safely, ensuring paths exist, permissions are correct, and data is written/read as expected.
---
- Resolve relative paths using `os.path.join` and `__file__` to avoid missing files.
- Check that the target directory exists; create it with `os.makedirs(..., exist_ok=True)` if needed.
- Open files with the correct mode (`'r'`, `'w'`, `'a'`, `'rb'`, `'wb'`) and encoding (`'utf-8'`).
- Use context managers (`with` statements) to guarantee file closure.
- Validate that the file content matches the required schema before processing.
- When writing CSV, include the header row and use the correct delimiter and quoting rules.
- Handle missing or malformed data gracefully, logging warnings instead of crashing.
- Ensure timestamps are converted to UTC and formatted as ISO‑8601 (`YYYY-MM-DDTHH:MM:SSZ`).
- Verify that numeric values are stored in the correct units (e.g., cents vs. dollars).
- After writing, confirm the file size is non‑zero and the file is readable.
