# 💼 Trình Phân Tích Phương Án Kinh Doanh AI

Ứng dụng Streamlit sử dụng AI (Gemini) để tự động trích xuất dữ liệu tài chính từ file Word, tính toán các chỉ số hiệu quả dự án và đưa ra phân tích chuyên sâu.

## ✨ Tính năng

- 🤖 **Trích xuất dữ liệu tự động**: Sử dụng Gemini AI để đọc và trích xuất thông tin từ file Word
- 📊 **Tính toán chỉ số tài chính**: NPV, IRR, PP, DPP
- 📈 **Trực quan hóa**: Biểu đồ dòng tiền, hoàn vốn, cấu trúc tài chính
- ✏️ **Chỉnh sửa dữ liệu**: Cho phép người dùng điều chỉnh dữ liệu AI trích xuất
- 🧠 **Phân tích AI**: Nhận xét và đánh giá từ AI về tính khả thi dự án
- 💾 **Cache thông minh**: Tránh gọi API lặp lại, tiết kiệm thời gian và chi phí

## 🚀 Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd new_project
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Lấy Gemini API Key

Truy cập [Google AI Studio](https://makersuite.google.com/app/apikey) để lấy API key miễn phí.

### 4. Cấu hình API Key (Tùy chọn)

**Cách 1: Sử dụng Streamlit Secrets (Khuyến nghị)**

Tạo file `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-api-key-here"
```

**Cách 2: Nhập trực tiếp trong ứng dụng**

Khi chạy ứng dụng, nhập API key vào ô input.

## 📖 Sử dụng

### 1. Chạy ứng dụng

```bash
streamlit run python.py
```

### 2. Chuẩn bị file Word

Tạo file `.docx` chứa thông tin phương án kinh doanh với các thông tin:

- **Vốn đầu tư ban đầu**: Số tiền đầu tư (VNĐ)
- **Dòng đời dự án**: Thời gian hoạt động (năm)
- **Doanh thu hàng năm**: Doanh thu trung bình/năm (VNĐ)
- **Chi phí hoạt động**: Chi phí trung bình/năm (VNĐ)
- **WACC**: Tỷ lệ chiết khấu (%)
- **Thuế suất**: Thuế TNDN (%)

**Ví dụ nội dung file Word:**

```
Phương án đầu tư nhà máy sản xuất

Vốn đầu tư: 5 tỷ đồng
Thời gian hoạt động: 10 năm
Doanh thu dự kiến: 2 tỷ đồng/năm
Chi phí vận hành: 1.2 tỷ đồng/năm
Chi phí sử dụng vốn (WACC): 12%
Thuế suất: 20%
```

### 3. Quy trình sử dụng

1. Upload file `.docx`
2. Nhập API key (nếu chưa cấu hình)
3. Nhấn "Lọc dữ liệu từ file Word"
4. Xem và chỉnh sửa dữ liệu nếu cần
5. Xem kết quả tính toán tự động
6. Nhấn "Phân tích các chỉ số hiệu quả" để nhận phân tích từ AI

## 📊 Các chỉ số tài chính

### NPV (Net Present Value)
- **Giá trị hiện tại ròng**: Tổng giá trị hiện tại của các dòng tiền
- **Đánh giá**: NPV > 0 → Dự án khả thi
- **Công thức**: `NPV = Σ [CFt / (1+r)^t]`

### IRR (Internal Rate of Return)
- **Tỷ suất hoàn vốn nội bộ**: Lãi suất làm NPV = 0
- **Đánh giá**: IRR > WACC → Dự án có lợi nhuận
- **Ý nghĩa**: Tỷ suất sinh lời nội tại của dự án

### PP (Payback Period)
- **Thời gian hoàn vốn**: Thời gian để thu hồi vốn đầu tư
- **Đánh giá**: Càng ngắn càng tốt
- **Công thức**: Năm cuối âm + (Số tiền còn thiếu / Dòng tiền năm sau)

### DPP (Discounted Payback Period)
- **Thời gian hoàn vốn có chiết khấu**: PP với dòng tiền đã chiết khấu
- **Đánh giá**: Chính xác hơn PP vì tính giá trị thời gian của tiền
- **Lưu ý**: Luôn dài hơn PP

## 🏗️ Cấu trúc dự án

```
new_project/
├── python.py                  # File chính - UI và logic điều khiển
├── config.py                  # Cấu hình và constants
├── validators.py              # Validation dữ liệu
├── ai_service.py              # Tương tác với Gemini AI
├── financial_calculator.py    # Tính toán tài chính
├── visualizations.py          # Tạo biểu đồ
├── utils.py                   # Các hàm tiện ích
├── requirements.txt           # Dependencies
└── README.md                  # Tài liệu này
```

## 🔧 Kiến trúc code

### Tách module rõ ràng
- **config.py**: Tập trung tất cả constants, prompts, messages
- **validators.py**: Validate và sanitize dữ liệu từ AI và user
- **ai_service.py**: Quản lý API calls với cache
- **financial_calculator.py**: Logic tính toán tài chính độc lập
- **visualizations.py**: Tách riêng code tạo biểu đồ
- **utils.py**: Document reading, session state management

### Cải tiến so với version 1.0

#### 1. ✅ Fix Cache Issue
```python
# Trước (Lỗi): dict không hashable
@st.cache_data
def calculate_financials(project_data: dict):
    ...

# Sau (Đúng): Sử dụng _self và cache tự động hash
@st.cache_data(show_spinner=False, ttl=3600)
def extract_project_data(_self, text: str):
    ...
```

#### 2. ✅ Fix File Upload Reset
```python
# Lưu file name trong session state để detect file mới
if (st.session_state.uploaded_file_name != uploaded_file.name):
    st.session_state.uploaded_file_name = uploaded_file.name
    SessionStateManager.reset_all_state()
```

#### 3. ✅ Better Error Handling
```python
# Trước: Try-except quá rộng
try:
    # 100 dòng code
except Exception as e:
    st.error(f"Error: {e}")

# Sau: Tách từng loại exception
is_valid, data, error_msg = DataValidator.validate_json_response(response_text)
if not is_valid:
    return False, None, error_msg
```

#### 4. ✅ Centralized Configuration
```python
# Model name chỉ định nghĩa 1 lần
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# Prompts tập trung trong config
EXTRACTION_PROMPT_TEMPLATE = """..."""
ANALYSIS_PROMPT_TEMPLATE = """..."""
```

#### 5. ✅ Enhanced UX
- Cho phép người dùng chỉnh sửa dữ liệu AI trích xuất
- Hiển thị hướng dẫn chi tiết khi chưa upload file
- Tooltips cho các chỉ số tài chính
- Better loading states và error messages

#### 6. ✅ Code Structure
```python
# Trước: 1 file 500 dòng
python.py (500 lines)

# Sau: 7 files module hóa
python.py (350 lines) - UI logic
config.py - Constants
validators.py - Validation
ai_service.py - AI API
financial_calculator.py - Calculations
visualizations.py - Charts
utils.py - Utilities
```

## 🐛 Debug & Troubleshooting

### Lỗi "API Key không hợp lệ"
- Kiểm tra API key có đúng từ Google AI Studio
- Đảm bảo không có khoảng trắng thừa

### Lỗi "Không thể trích xuất JSON"
- File Word có thể không chứa đủ thông tin
- Thử chỉnh sửa thủ công bằng checkbox "Chỉnh sửa dữ liệu"

### Lỗi "IRR không thể tính"
- Xảy ra khi dòng tiền không đổi dấu (toàn dương hoặc toàn âm)
- Kiểm tra lại vốn đầu tư và doanh thu

### Biểu đồ không hiển thị
- Kiểm tra internet connection (Plotly cần CDN)
- Thử refresh trang

## 🔐 Bảo mật

- ⚠️ **Không commit API key** vào Git
- ✅ Sử dụng `.streamlit/secrets.toml` (đã trong `.gitignore`)
- ✅ API key được nhập qua `type="password"`

## 📝 License

MIT License - Tự do sử dụng và chỉnh sửa

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:
1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📧 Liên hệ

Phát triển bởi AI | Powered by Gemini & Streamlit

---

**Lưu ý**: Ứng dụng này chỉ mang tính chất tham khảo. Đối với quyết định đầu tư thực tế, vui lòng tham khảo ý kiến chuyên gia tài chính.
