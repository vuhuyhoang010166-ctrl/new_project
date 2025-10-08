# 🎨 Giao diện mới - Phong cách ECharts Demo

## 🚀 Chạy ứng dụng

### Option 1: Giao diện mới (ECharts style)
```bash
streamlit run app.py
```

### Option 2: Giao diện cũ (Classic)
```bash
streamlit run python.py
```

## ✨ Tính năng giao diện mới

### 🎨 Design Modern
- **Dark Theme**: Nền tối chuyên nghiệp như ECharts Demo
- **Sidebar Configuration**: Panel bên trái với dropdown chọn phương án
- **Full-width Charts**: Biểu đồ hiển thị toàn màn hình
- **Responsive Layout**: Tự động điều chỉnh theo kích thước màn hình

### 📋 Sidebar Features

#### ⚙️ Configuration Section
- **API Key Management**: Input API key với validation
- **Analysis Options**: Dropdown với 5 lựa chọn:
  - 📄 Upload File Word mới
  - 📊 Ví dụ 1: Nhà máy sản xuất (Vốn 5 tỷ, 10 năm)
  - 🏭 Ví dụ 2: Dự án bất động sản (Vốn 50 tỷ, 15 năm)
  - 🏪 Ví dụ 3: Cửa hàng kinh doanh (Vốn 500 tr, 7 năm)
  - 💼 Ví dụ 4: Startup công nghệ (Vốn 2 tỷ, 5 năm)

#### ⚡ Quick Actions
- 🔄 **Reset toàn bộ**: Xóa tất cả dữ liệu và bắt đầu lại
- 📖 **Hướng dẫn**: Hiển thị guide chi tiết

#### ℹ️ Info Panel
- Version number
- Powered by info
- Copyright

### 📊 Main Content Area

#### Header
- Title lớn, nổi bật ở giữa màn hình
- Icon và styling chuyên nghiệp

#### Data Display
- **6-column metrics**: Hiển thị thông tin dự án trong 6 cột đều nhau
- **Expandable editor**: Form chỉnh sửa dữ liệu có thể thu gọn
- **4-column indicators**: NPV, IRR, PP, DPP với màu sắc và delta

#### Visualizations
- Biểu đồ dòng tiền (Bar chart với màu động)
- Dòng tiền lũy kế (Line chart với breakeven)
- So sánh doanh thu/chi phí (Mixed chart)
- NPV gauge chart
- IRR vs WACC comparison
- Cấu trúc tài chính (Donut chart)

#### AI Analysis
- Button trigger với spinner
- Info box hiển thị kết quả
- Cache để tránh gọi API lặp lại

## 🎨 Color Scheme

```css
Primary Color: #0066cc (Blue)
Background: #0e1117 (Dark)
Secondary BG: #1a1d26 (Darker)
Text: #ffffff (White)
Border: #2d3142 (Gray)
```

## 📱 Responsive Breakpoints

- **Desktop**: Full sidebar + wide content
- **Tablet**: Collapsible sidebar
- **Mobile**: Hidden sidebar (hamburger menu)

## 🔧 Customization

### Thay đổi màu chủ đạo
Edit file [.streamlit/config.toml](.streamlit/config.toml):
```toml
[theme]
primaryColor = "#0066cc"  # Đổi thành màu bạn muốn
```

### Thay đổi CSS
Edit phần `st.markdown("""<style>...</style>""")` trong [app.py](app.py)

### Thêm ví dụ mới
Edit hàm `load_example_data()` trong [app.py](app.py):
```python
"📌 Ví dụ 5: Tên dự án": {
    'von_dau_tu': 1000000000,
    'dong_doi_du_an': 8,
    'doanh_thu_nam': 500000000,
    'chi_phi_nam': 300000000,
    'wacc': 12.0,
    'thue_suat': 20.0
}
```

## 🆚 So sánh 2 phiên bản

| Feature | python.py (Classic) | app.py (Modern) |
|---------|-------------------|-----------------|
| Layout | Top-down | Sidebar + Main |
| Theme | Light/Dark toggle | Dark only |
| Examples | No | 4 built-in |
| File Upload | Required | Optional |
| Quick Actions | No | Yes |
| Help Section | Expander at bottom | Button in sidebar |
| Metrics Display | 3-3 columns | 6 columns |
| Edit Form | Always visible | Expandable |
| Navigation | Scroll | Sidebar menu |

## 🐛 Known Issues

### Dark theme không áp dụng hoàn toàn
**Fix**: Thêm theme trong config.toml và custom CSS

### Sidebar bị thu gọn khi refresh
**Fix**: Set `initial_sidebar_state="expanded"` trong `st.set_page_config()`

### Biểu đồ bị lỗi font
**Fix**: Dùng font mặc định `sans serif` trong config.toml

## 📸 Screenshots

Layout tương tự như ảnh bạn gửi:
- Sidebar trái với Configuration
- Dropdown chọn examples
- Main content với biểu đồ full-width
- Dark theme chuyên nghiệp

## 🎯 Next Features (Coming Soon)

- [ ] Export kết quả ra PDF
- [ ] So sánh nhiều dự án cùng lúc
- [ ] Dark/Light theme toggle
- [ ] Multi-language support
- [ ] Save/Load project sessions
- [ ] Advanced filtering trong sidebar
- [ ] Real-time collaboration

## 📞 Support

Nếu có vấn đề, hãy kiểm tra:
1. API Key đã nhập đúng chưa
2. File Word có đúng format không
3. Internet connection (cho Plotly CDN)
4. Dependencies đã cài đủ chưa (`pip install -r requirements.txt`)

---

Enjoy your new modern UI! 🚀
