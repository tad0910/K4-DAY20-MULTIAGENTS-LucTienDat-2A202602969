"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Delegate to this subagent when you need to explore workspace structure, "
                "read documentation, docstrings, schema definitions, inspect log samples or "
                "diagnose error roots without making any modifications. Provide exact paths "
                "and what specific facts to find. Returns a factual findings report."
            ),
            "system_prompt": (
                "You are an exploratory research subagent. Your role is strictly read-only inspection: "
                "read files, search patterns, analyze code structure, and identify root causes. "
                "Do NOT modify or delete any files in the workspace. Return a clear and concise report of your findings."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Delegate to this subagent when you need to write or edit source code, fix identified bugs, "
                "clean and process data files, or generate required output files and run tests. "
                "Provide all task rules, file paths, and target requirements. Returns a summary of changes and execution results."
            ),
            "system_prompt": (
                "You are an implementation subagent. Your role is to write clean code, clean datasets, "
                "apply bug fixes, and run shell commands or tests to verify your implementation. "
                "Carefully follow all specified rules and formats. In your final report, summarize what you created or changed."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Delegate to this subagent when tasks or changes are completed and you need an independent "
                "verification against all problem requirements, edge cases, formatting constraints, and tests. "
                "Provide the task specification and expected outputs. Returns a detailed verification assessment."
            ),
            "system_prompt": (
                "You are an independent verification subagent. Your role is to validate that the solution "
                "fully satisfies all task instructions, output files exist in correct formats, and tests pass. "
                "Do NOT modify files; report any discrepancies or confirm full compliance."
            ),
        },
    ]
