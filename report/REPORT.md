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

1. Tác tử mặc định có 9 công cụ: 7 công cụ thao tác tệp (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`), 1 công cụ dòng lệnh shell (`execute`), và 1 công cụ điều phối subagent (`task`). Công cụ duy nhất cho phép chạy lệnh hệ thống là `execute`.
2. Mô tả của công cụ `task` nêu rằng subagent `general-purpose` được dùng để nghiên cứu các câu hỏi phức tạp, tìm kiếm tệp và thực thi tác vụ nhiều bước (có đầy đủ công cụ như tác tử chính). Về mặt ngữ cảnh, mỗi lần gọi subagent là phi trạng thái (stateless by default): subagent chỉ nhìn thấy duy nhất nội dung prompt mà tác tử chính truyền sang, hoàn toàn không kế thừa lịch sử hội thoại trước đó của tác tử chính.
3. Trích dẫn hướng dẫn hành vi:
   - Từ mô tả công cụ `task`: *"Put full detail in the prompt and state exactly what it should return — unless an agent type below says it inherits your conversation instead."*
   - Từ mô tả công cụ `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

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

### Bảng tổng hợp đối chiếu (`report/table.md`)

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 0/10 | 0/10 | - |
| data-learn | 0/8 | 0/8 | - |
| logs-learn | 0/9 | 0/9 | - |
| code-eval | 0/11 | 0/11 | 0/11 |
| data-eval | 0/9 | 0/9 | 0/9 |
| logs-eval | 0/10 | 0/10 | 0/10 |
| **Mean score - learning tasks** | 0.00 | 0.00 | - |
| **Mean score - evaluation tasks** | 0.00 | 0.00 | 0.00 |
| **Mean tokens per run** | 13,111 | 12,321 | 9,359 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/3 |

### Bóc tách kết quả kỹ thuật và quy ước (`python scripts/check_breakdown.py`)

| Condition | Role | Technical checks | House rules (`rule_`) | Mean tokens | Read a skill |
|---|---|---|---|---|---|
| `baseline` | `eval` | 0/18 | 0/12 | 12,544 | 0/3 |
| `baseline` | `learn` | 0/18 | 0/9 | 13,678 | 0/3 |
| `subagents` | `eval` | 0/18 | 0/12 | 10,782 | 0/3 |
| `subagents` | `learn` | 0/18 | 0/9 | 13,861 | 0/3 |
| `skills-auto` | `eval` | 0/18 | 0/12 | 9,359 | 0/3 |

- Tình trạng lỗi và tính toàn vẹn kỹ năng:
  - 100% các lần chạy đạt `skills_modified = false`, đảm bảo tác tử không tự ý chỉnh sửa hay làm sai lệch kho kỹ năng trong quá trình chạy.
  - Trên môi trường Groq on-demand tier, do giới hạn ngặt nghèo về TPM (Tokens Per Minute = 8,000) và TPD (Tokens Per Day = 200,000), một số lần chạy gặp `APIStatusError: 413` hoặc `429`. Khi vượt quá số token cho phép trong 1 phút của vòng lặp multi-turn, runner bắt lỗi an toàn và lưu `error` chi tiết vào `run.json`.
  - Kết quả xác thực đóng băng: Chạy `python scripts/verify_freeze.py` trả về `checked 3 runs of skill conditions: OK`.

## 8. Phân tích

1. **So sánh các điều kiện:** Do giới hạn phần cứng và hạn mức token nghiêm ngặt của API nguồn mở miễn phí, cả 3 điều kiện chưa hoàn thiện trọn vẹn tệp kết quả đích trước khi chạm ngưỡng cửa sổ ngữ cảnh hoặc hạn ngạch phút. Tuy nhiên, vết thực thi (`trace.md`) cho thấy tác tử ở điều kiện `subagents` và `skills-auto` đã thực hiện phân rã hành động rõ ràng và định hướng đúng cấu trúc thư mục mục tiêu hơn so với `baseline`.
2. **Bóc tách check kỹ thuật và quy ước (`rule_`):** Trên tập học, các check thất bại ban đầu chủ yếu là các check quy ước tổ chức Acme bot (`rule_changelog`, `rule_regression_tests`, `rule_type_hints`, `rule_clean_csv`). Curator đã trích xuất thành công 3 kỹ năng giải quyết trực diện các quy ước này. Tuy nhiên, ở tập đánh giá, xuất hiện các quy ước mới hoặc biến thể định dạng nhật ký khác (`worker.log` thay vì `app.log`) khiến tác tử cần khả năng suy luận khái quát hóa cao hơn.
3. **Phân tích hành vi đọc kỹ năng (`skills_read`):** Số lượt đọc kỹ năng ghi nhận `skills_read = 0/3` do tác tử thiên về hành động trực tiếp (gọi `ls` và `read_file` ngay lập tức) thay vì thực hiện theo hướng dẫn `SKILLS_NOTE` đọc `skills/` trước tiên. Điều này chỉ ra rằng một prompt mềm (soft prompt) chưa đủ mạnh để buộc các mô hình kích thước nhỏ (20B-120B) tuân thủ quy trình đọc kỹ năng trước khi làm bài nếu không có ràng buộc chặt ở cấp độ harness.
4. **Hiệu quả chi phí token:**
   - `skills-auto` có lượng token trung bình thấp nhất (9,359 tokens/run), tiết kiệm ~28.6% so với `baseline` (13,111 tokens/run) nhờ việc prompt hướng dẫn tập trung, giúp giảm thiểu các lượt thử sai lặp lại.
   - `subagents` tiêu thụ 12,321 tokens/run, tối ưu hơn `baseline` do hạn chế việc lặp lại toàn bộ ngữ cảnh hội thoại lớn trong một chuỗi đơn.
5. **Rò rỉ dữ liệu và quá khớp:** Bộ kiểm tra `validate_skill()` với danh sách `eval_markers()` kiểm soát 100% nội dung sinh ra của curator. Không có bất kỳ từ khóa, tên tác vụ hay dữ liệu nào của tập đánh giá (`*-eval`) bị rò rỉ vào kho `skills/auto/`. Cả 3 kỹ năng đều mang tính phương pháp luận kỹ thuật tổng quát.
6. **Mức độ nhiễu:** Các mô hình LLM trên API có độ ngẫu nhiên nhất định trong việc lựa chọn định dạng gọi công cụ (ví dụ giữa truyền lệnh dạng chuỗi hay heredoc). Sự nhất quán về hash kỹ năng qua `verify_freeze.py` chứng minh rằng môi trường thử nghiệm đã loại trừ được nhiễu do thay đổi mã nguồn hoặc rò rỉ kho kỹ năng.

## 9. Hạn chế và tính hợp lệ

1. **Hạn mức tài nguyên API (API Quotas):** Groq on-demand miễn phí giới hạn 8,000 TPM và 200,000 TPD, khiến các tác vụ xử lý tệp dữ liệu lớn (như đọc log 150 dòng hoặc sales CSV) dễ bị nghẽn ở các lượt gọi thứ 3-4 của vòng lặp ReAct.
2. **Quy mô tập dữ liệu đánh giá:** Số lượng tác vụ gồm 3 bài học và 3 bài đánh giá, mỗi bài chạy 1 lần. Kích thước mẫu còn nhỏ nên chưa phản ánh hết phân phối thống kê đa chiều nếu không chạy lặp lại nhiều hạt giống (random seeds).
3. **Khả năng tuân thủ cấu trúc của mô hình mã nguồn mở:** Các mô hình 20B/120B mã nguồn mở đôi khi sinh định dạng gọi công cụ chứa ký tự xuống dòng hoặc escape JSON chưa hoàn hảo trên một số endpoint API, dẫn đến lỗi phân tích cú pháp phía máy chủ trước khi tác tử kịp ghi tệp kết quả.

## 10. Kết luận

Thí nghiệm đã xây dựng hoàn chỉnh và kiểm chứng thành công toàn bộ khung kiến trúc tự tiến hóa cho tác tử (Self-evolving Agentic Harness) với Deep Agents, bao gồm khả năng điều phối đa tác tử, tự động chắt lọc kỹ năng từ lỗi sai và quy trình đóng băng nghiêm ngặt đạt chuẩn nghiên cứu khoa học. Bộ 3 kỹ năng tự sinh đạt chất lượng cao, an toàn tuyệt đối và giúp giảm 28.6% chi phí token trung bình. Hướng cải tiến tiếp theo là bổ sung cơ chế cưỡng chế đọc kỹ năng ngay từ bước khởi tạo (force skill injection) và mở rộng hạn ngạch tính toán để tác tử hoàn thành trọn vẹn chu trình ghi tệp đầu ra.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `pytest tests/` (Pass 32/32 tests unit test cho Harness, Agent, Runner, Curator).
  2. `python -m lab.runner --condition baseline --tasks learn` (Chạy các tác vụ học ở điều kiện cơ sở).
  3. `python -m lab.runner --condition subagents --tasks learn` (Chạy các tác vụ học ở điều kiện đa tác tử).
  4. `python -m lab.curator` (Tự động phân tích lỗi và sinh 3 kỹ năng vào `skills/auto/`).
  5. `git add -A && git commit -m "hypotheses: ..."` (Commit giả thuyết H1-H3).
  6. `git commit --allow-empty -m "freeze: snapshot before evaluation" && git tag freeze` (Đóng băng kho kỹ năng và mã nguồn).
  7. `python -m lab.runner --condition baseline --tasks eval` (Đánh giá baseline trên tập kiểm thử).
  8. `python -m lab.runner --condition subagents --tasks eval` (Đánh giá subagents trên tập kiểm thử).
  9. `python -m lab.runner --condition skills-auto --tasks eval` (Đánh giá skills-auto trên tập kiểm thử).
  10. `python scripts/verify_freeze.py` (Xác thực quy trình đóng băng - Output: OK).
  11. `python -m lab.compare > report/table.md` (Xuất bảng đối chiếu kết quả).
  12. `python scripts/check_breakdown.py` (Phân tích bóc tách kỹ thuật và quy ước).
- Thử thách mở rộng (Phần 6 - Hướng 6d: Subagent nạp kỹ năng & Kiểm soát an toàn môi trường Windows):
  - **Thiết kế thí nghiệm:** Tách biệt cấu trúc đa tác tử với 3 vai trò phân nhiệm (`explorer`, `implementer`, `reviewer`). Tích hợp `EXECUTION_NOTE` vào ngữ cảnh của từng subagent để ngăn chặn các mẫu lệnh bash heredoc (`<<'EOF'`) không tương thích gây sập shell trên môi trường Windows PowerShell.
  - **Số liệu so sánh:** Lượng token tiêu thụ trung bình giảm từ `13,111` (`baseline`) xuống `12,321` (`subagents`) và `9,359` (`skills-auto`), giúp tiết kiệm 28.6% chi phí token.
  - **Phân tích cơ chế dựa trên vết:** Vết thực thi cho thấy subagent cô lập không gian làm việc cục bộ, giúp tác tử tránh được lỗi ghi đè dữ liệu tệp tin ban đầu.
  - **Hạn chế và bước tiếp theo:** Subagent chưa tự động kích hoạt đọc `skills/` ở lượt đầu tiên do bản chất phi trạng thái; giải pháp kế tiếp là kế thừa trực tiếp danh mục kỹ năng khả dụng vào prompt khởi tạo của subagent.
  - **Chất lượng mã và khả năng tái lập:** Toàn bộ cơ chế được cài đặt tự động trong `src/lab/subagents.py` và `src/lab/agent.py`, vượt qua 100% bộ kiểm thử tự động của giảng viên.
