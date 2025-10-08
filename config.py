# -*- coding: utf-8 -*-
"""
File cấu hình cho ứng dụng Phân tích Phương án Kinh doanh
"""

# === GEMINI AI CONFIG ===
GEMINI_MODEL_NAME = "gemini-2.5-flash"
GEMINI_API_TIMEOUT = 60  # seconds

# === APP CONFIG ===
APP_TITLE = "Trình Phân Tích Phương Án Kinh Doanh"
APP_ICON = "💼"
PAGE_LAYOUT = "wide"

# === FINANCIAL DEFAULTS ===
DEFAULT_VALUES = {
    "von_dau_tu": 0,
    "dong_doi_du_an": 0,
    "doanh_thu_nam": 0,
    "chi_phi_nam": 0,
    "wacc": 0,
    "thue_suat": 0
}

# === EXTRACTION PROMPT ===
EXTRACTION_PROMPT_TEMPLATE = """
Bạn là một chuyên gia phân tích tài chính. Hãy đọc kỹ văn bản phương án kinh doanh dưới đây.
Trích xuất chính xác các thông tin sau và trả về dưới dạng một đối tượng JSON duy nhất.
Nếu không tìm thấy thông tin nào, hãy trả về giá trị 0 cho trường đó.

1. "von_dau_tu": Tổng vốn đầu tư ban đầu (đơn vị: VNĐ).
2. "dong_doi_du_an": Dòng đời dự án (đơn vị: năm).
3. "doanh_thu_nam": Doanh thu trung bình hàng năm (đơn vị: VNĐ).
4. "chi_phi_nam": Chi phí hoạt động trung bình hàng năm (không bao gồm vốn đầu tư ban đầu) (đơn vị: VNĐ).
5. "wacc": Tỷ lệ chiết khấu hoặc chi phí sử dụng vốn bình quân (WACC) (đơn vị: phần trăm, ví dụ: 12.5 cho 12.5%).
6. "thue_suat": Thuế suất thuế thu nhập doanh nghiệp (đơn vị: phần trăm, ví dụ: 20 cho 20%).

Văn bản cần phân tích:
---
{text}
---

Hãy đảm bảo kết quả chỉ là một đối tượng JSON hợp lệ, không có bất kỳ văn bản giải thích nào khác.
Ví dụ định dạng đầu ra:
{{
  "von_dau_tu": 5000000000,
  "dong_doi_du_an": 5,
  "doanh_thu_nam": 3000000000,
  "chi_phi_nam": 1500000000,
  "wacc": 12.5,
  "thue_suat": 20
}}
"""

# === ANALYSIS PROMPT ===
ANALYSIS_PROMPT_TEMPLATE = """
Với vai trò là một chuyên gia tư vấn đầu tư, hãy phân tích dự án kinh doanh dưới đây dựa trên các thông tin và chỉ số tài chính.
Đưa ra nhận định chuyên môn về tính khả thi của dự án.

**THÔNG TIN DỰ ÁN:**
- Vốn đầu tư ban đầu: {von_dau_tu} VNĐ
- Thời gian hoạt động: {dong_doi} năm
- Doanh thu dự kiến/năm: {doanh_thu} VNĐ
- Chi phí vận hành/năm: {chi_phi} VNĐ
- Chi phí sử dụng vốn (WACC): {wacc}%
- Thuế suất: {thue_suat}%

**CÁC CHỈ SỐ HIỆU QUẢ:**
- Giá trị hiện tại ròng (NPV): {npv} VNĐ
- Tỷ suất hoàn vốn nội bộ (IRR): {irr}
- Thời gian hoàn vốn (PP): {pp}
- Thời gian hoàn vốn có chiết khấu (DPP): {dpp}

**YÊU CẦU PHÂN TÍCH:**
1. Đánh giá từng chỉ số tài chính (NPV, IRR, PP, DPP) trong bối cảnh dự án này
2. So sánh IRR với WACC để đánh giá hiệu quả đầu tư
3. Phân tích khả năng sinh lời dựa trên doanh thu và chi phí
4. Đưa ra kết luận tổng quan về tính khả thi (rất khả thi / khả thi / cần cân nhắc / rủi ro cao / không khả thi)
5. Đề xuất các khuyến nghị (nếu có)

Hãy trình bày câu trả lời một cách chuyên nghiệp, có cấu trúc rõ ràng với các đề mục cho từng phần.
"""

# === UI TEXT ===
UI_TEXTS = {
    "upload_label": "1. Tải lên file phương án kinh doanh (.docx)",
    "api_key_found": "Đã tìm thấy API Key.",
    "api_key_input": "Hoặc nhập Gemini API Key của bạn vào đây:",
    "extract_button": "Lọc dữ liệu từ file Word",
    "extract_loading": "AI đang đọc và phân tích file... Vui lòng chờ trong giây lát...",
    "extract_success": "✅ AI đã trích xuất thành công dữ liệu!",
    "calculate_loading": "Đang xây dựng bảng dòng tiền và tính toán các chỉ số...",
    "analyze_button": "Phân tích các chỉ số hiệu quả",
    "analyze_loading": "AI đang soạn thảo phân tích chuyên môn...",
    "no_file_warning": "Vui lòng tải lên file .docx và đảm bảo đã cung cấp API Key để bắt đầu.",
}

# === ERROR MESSAGES ===
ERROR_MESSAGES = {
    "api_error": "Lỗi khi gọi API của AI: {}",
    "json_parse_error": "Không thể phân tích JSON từ AI. Phản hồi: {}",
    "invalid_data": "Dữ liệu đầu vào không hợp lệ để tính toán. Lỗi: {}",
    "file_read_error": "Không thể đọc file: {}",
    "calculation_error": "Lỗi khi tính toán các chỉ số tài chính: {}",
}
