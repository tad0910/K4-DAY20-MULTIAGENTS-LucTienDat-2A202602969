# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Lục Tiến Đạt | 2A202602969 | Hoàn thành toàn bộ: Agent Harness, Subagents, Runner, Curator, Freeze protocol, Thử nghiệm & Báo cáo (100%) |

- Nhà cung cấp và mô hình: Groq API (`LAB_BASE_URL=https://api.groq.com/openai/v1`), `LAB_MODEL=openai/gpt-oss-20b`, `LAB_TEMPERATURE=0`, `recursion_limit=30`
- Phiên bản Deep Agents: `deepagents 0.2.x`, Hệ điều hành: Windows 11 (PowerShell), chạy trực tiếp trong virtual environment (`.venv`)
- Số lần chạy tác vụ đã dùng / ngân sách: 12 / 30 lần chạy
- Commit của tag `freeze`: `freeze` (sau commit hypotheses)

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1: Ở tác vụ đánh giá (eval), điều kiện subagents sẽ phân tách ngữ cảnh giữa các vai trò (kỹ sư thăm dò, cài đặt, thẩm định) giúp giảm thiểu các lỗi thao tác nhầm trên tệp tin nhưng làm tăng đáng kể tổng lượng token tiêu thụ so với baseline do chi phí điều phối đa tác tử.
- H2: Điều kiện skills-auto sẽ đạt điểm số cao hơn baseline trên tác vụ đánh giá nhờ bộ kỹ năng tự sinh (spec-compliance, file-management, testing-best-practices) đã chắt lọc các quy ước ẩn của Acme (RFC 4180 quoting, type hints, changelog, UTC ISO-8601) từ các lần chạy học thất bại.
- H3: Điểm số trung bình trên tác vụ đánh giá (eval) sẽ có xu hướng thấp hơn tác vụ học (learn) do tập dữ liệu đánh giá chứa các trường hợp biên mới chưa từng xuất hiện và các bài kiểm tra đòi hỏi tính khái quát hoá cao hơn.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử Deep Agents sử dụng vòng lặp ReAct tích hợp sẵn các công cụ thao tác tệp tin (`read_file`, `write_file`, `edit_file`), thực thi dòng lệnh (`execute`) và công cụ giao việc (`task`).
2. Môi trường thực thi được cô lập an toàn thông qua `LocalShellBackend(root_dir=sandbox)` với cơ chế ẩn toàn bộ khóa API môi trường (`LAB_API_KEY`, `OPENAI_API_KEY`, v.v.) khỏi shell của tác tử.
3. Khi nạp `skills/`, Deep Agents tự động gắn đường dẫn kỹ năng vào ngữ cảnh hệ thống và hướng dẫn tác tử đọc các tệp `SKILL.md` áp dụng tương ứng trước khi thực thi.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `rule_changelog` | E. Vi phạm quy ước tổ chức | `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets).` |
| `code-learn` | `rule_regression_tests` | E. Vi phạm quy ước tổ chức | `RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass.` |
| `code-learn` | `rule_type_hints` | E. Vi phạm quy ước tổ chức | `RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value.` |
| `code-learn` | `parse_price_all_formats` | D. Bỏ sót dữ liệu bẩn hoặc định dạng | `wrong for: ['$1,299.50', '(12.00)', '$1,000,000.00']` |
| `code-learn` | `discount_rounds_half_up` | A. Bỏ qua đặc tả | `wrong for: [('10.05', 10, '9.05'), ('0.05', 50, '0.03'), ('2.665', 0, '2.67')]` |
| `data-learn` | `rule_clean_csv` | E. Vi phạm quy ước tổ chức | `RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents...` |
| `data-learn` | `rule_money_in_cents` | E. Vi phạm quy ước tổ chức | Bot yêu cầu đơn vị tiền tệ quy đổi ra integer cents |
| `logs-learn` | `rule_service_names` | E. Vi phạm quy ước tổ chức | Quy ước chuẩn hóa định dạng service name theo Acme bot |

Nhận xét: Nhóm lỗi E (Vi phạm quy ước tổ chức) chiếm đa số tuyệt đối (hơn 60% các check thất bại). Tác tử không thể tự biết các quy ước riêng của tổ chức Acme nếu chỉ dựa vào đề bài ban đầu. Kỹ năng (skill) do curator sinh ra hoàn toàn có thể phòng ngừa triệt để nhóm lỗi E này bằng cách mã hóa các quy ước `rule_` thành checklist hành động bắt buộc.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa:
  1. `explorer`: Chuyên đọc cấu trúc thư mục (`ls`), kiểm tra tệp tin, phân tích định dạng dữ liệu đầu vào.
  2. `implementer`: Chuyên lập trình, sửa mã nguồn, viết mã xử lý nghiệp vụ theo đặc tả.
  3. `reviewer`: Chuyên chạy kiểm thử độc lập (`pytest`), rà soát quy chuẩn Acme bot trước khi nộp bài.
- `subagent_calls` ở từng tác vụ và nhận xét:
  - Ở các tác vụ đơn giản hoặc khi tác tử chính xử lý trực tiếp các bước dòng lệnh ban đầu, `subagent_calls` có thể bằng 0 do tác tử tự tin hoàn thành mà không phân rã nhiệm vụ.
  - Khi ủy quyền, tác tử cần cung cấp toàn bộ đường dẫn và quy tắc vào lời gọi con do subagent không kế thừa prompt gốc.
- Ảnh hưởng đến token và thời gian: Chế độ `subagents` có tổng token (~14,070 tokens trên `code-learn`) cao hơn nhẹ so với `baseline` (~12,939 tokens) do việc nạp thêm mô tả vai trò subagents vào prompt điều phối. Thời gian phản hồi tăng do quy trình phân luồng.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator: 2 lần. Không có skill nào bị xóa. Cả 3 kỹ năng đều vượt qua 100% các bước kiểm tra an toàn nghiêm ngặt của `validate_skill()`.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `spec-compliance` | Tổng quát | Đúng. Hướng dẫn chi tiết đối chiếu docstring, định dạng xuất dữ liệu (RFC 4180 quoting), quy tắc làm tròn số half-up | 15 dòng, mô tả súc tích < 200 ký tự |
| `file-management` | Tổng quát | Đúng. Hướng dẫn an toàn I/O, tạo thư mục cha, chuẩn hóa múi giờ UTC ISO-8601, chuyển đổi đơn vị cents | 15 dòng, mô tả súc tích < 200 ký tự |
| `testing-best-practices` | Tổng quát | Đúng. Bổ sung type annotations, thêm file `tests/test_regressions.py`, cập nhật `CHANGELOG.md` dưới mục `## Unreleased` | 15 dòng, mô tả súc tích < 200 ký tự |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
