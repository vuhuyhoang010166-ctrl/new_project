# -*- coding: utf-8 -*-
"""
Tên ứng dụng: Trình Phân Tích Phương Án Kinh Doanh
Version: 2.0 - Modern UI with Sidebar
"""

import streamlit as st
from config import APP_TITLE, APP_ICON, UI_TEXTS
from utils import (
    DocumentReader,
    SessionStateManager,
    DataFormatter,
    get_api_key_from_secrets_or_input
)
from ai_service import get_ai_service
from financial_calculator import calculate_project_financials
from visualizations import ProjectVisualizer


# === CẤU HÌNH TRANG ===
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CUSTOM CSS ===
st.markdown("""
<style>
    /* Dark theme styling */
    .main {
        background-color: #0e1117;
    }

    /* Title styling */
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 2rem;
        padding: 2rem 0;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1d26;
        padding: 2rem 1rem;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }

    /* Sidebar headers */
    .sidebar-header {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        background-color: #0066cc;
        color: white;
        border: none;
        padding: 0.75rem 1rem;
        font-weight: 500;
        transition: all 0.3s;
    }

    .stButton > button:hover {
        background-color: #0052a3;
        border: none;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1e2130;
        border-radius: 5px;
        font-weight: 500;
    }

    /* Info box */
    .stAlert {
        background-color: #1e2130;
        border-left: 4px solid #0066cc;
    }

    /* Selectbox */
    .stSelectbox {
        margin-bottom: 1.5rem;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #1e2130;
        border-radius: 5px;
        padding: 1rem;
    }

    /* Remove padding from main content */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Divider */
    hr {
        margin: 2rem 0;
        border-color: #2d3142;
    }

    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #ffffff;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #0066cc;
    }
</style>
""", unsafe_allow_html=True)

# === KHỞI TẠO SESSION STATE ===
SessionStateManager.initialize_session_state()

# === SIDEBAR CONFIGURATION ===
with st.sidebar:
    st.markdown('<p class="sidebar-header">⚙️ Configuration</p>', unsafe_allow_html=True)

    # API Key Section
    st.markdown("**🔑 API Key**")
    api_key = get_api_key_from_secrets_or_input()

    st.markdown("---")

    # Choose Example Section
    st.markdown("**📁 Chọn phương án phân tích**")

    analysis_options = [
        "📄 Upload File Word mới",
        "📊 Ví dụ 1: Nhà máy sản xuất",
        "🏭 Ví dụ 2: Dự án bất động sản",
        "🏪 Ví dụ 3: Cửa hàng kinh doanh",
        "💼 Ví dụ 4: Startup công nghệ"
    ]

    selected_example = st.selectbox(
        "Chọn một phương án:",
        analysis_options,
        key="example_selector"
    )

    st.markdown("---")

    # File Upload Section
    if selected_example == "📄 Upload File Word mới":
        st.markdown("**📤 Upload File**")
        uploaded_file = st.file_uploader(
            "Chọn file .docx",
            type=['docx'],
            help="Chọn file Word chứa phương án kinh doanh",
            label_visibility="collapsed"
        )
    else:
        uploaded_file = None
        st.markdown("**ℹ️ Đang sử dụng dữ liệu mẫu**")
        st.info(f"Bạn đang xem: {selected_example}")

    st.markdown("---")

    # Quick Actions
    st.markdown("**⚡ Quick Actions**")
    if st.button("🔄 Reset toàn bộ"):
        SessionStateManager.reset_all_state()
        st.rerun()

    if st.button("📖 Hướng dẫn"):
        st.session_state.show_help = True

    st.markdown("---")

    # Info
    st.markdown("**ℹ️ Thông tin**")
    st.caption("Version: 2.0")
    st.caption("Powered by Gemini AI")
    st.caption("© 2024 Business Analyzer")

# === MAIN CONTENT ===

# Header
st.markdown(f'<h1 class="main-title">{APP_ICON} {APP_TITLE}</h1>', unsafe_allow_html=True)

# Help Section (if requested)
if 'show_help' not in st.session_state:
    st.session_state.show_help = False

if st.session_state.show_help:
    with st.expander("📖 Hướng dẫn chi tiết", expanded=True):
        col1, col2, col3 = st.columns([1, 8, 1])
        with col2:
            st.markdown("""
            ### 🚀 Cách sử dụng ứng dụng:

            **Bước 1: Cấu hình**
            - Nhập API Key từ Google AI Studio
            - Chọn phương án phân tích (Upload file hoặc dùng ví dụ mẫu)

            **Bước 2: Upload hoặc chọn dữ liệu**
            - Upload file Word (.docx) chứa thông tin dự án
            - Hoặc chọn một trong các ví dụ mẫu

            **Bước 3: Trích xuất dữ liệu**
            - Nhấn nút "Trích xuất dữ liệu"
            - AI sẽ tự động đọc và phân tích

            **Bước 4: Xem kết quả**
            - Kiểm tra dữ liệu đã trích xuất
            - Chỉnh sửa nếu cần
            - Xem bảng dòng tiền và các chỉ số tài chính
            - Phân tích biểu đồ trực quan
            - Nhận đánh giá từ AI

            ---

            ### 📊 Các chỉ số tài chính:

            - **NPV**: Giá trị hiện tại ròng (NPV > 0 là tốt)
            - **IRR**: Tỷ suất hoàn vốn nội bộ (IRR > WACC là tốt)
            - **PP**: Thời gian hoàn vốn (càng ngắn càng tốt)
            - **DPP**: Thời gian hoàn vốn có chiết khấu
            """)

        if st.button("✖️ Đóng hướng dẫn"):
            st.session_state.show_help = False
            st.rerun()

# === LOAD EXAMPLE DATA ===
def load_example_data(example_name):
    """Load dữ liệu mẫu dựa trên lựa chọn"""
    examples = {
        "📊 Ví dụ 1: Nhà máy sản xuất": {
            'von_dau_tu': 5000000000,
            'dong_doi_du_an': 10,
            'doanh_thu_nam': 2000000000,
            'chi_phi_nam': 1200000000,
            'wacc': 12.0,
            'thue_suat': 20.0
        },
        "🏭 Ví dụ 2: Dự án bất động sản": {
            'von_dau_tu': 50000000000,
            'dong_doi_du_an': 15,
            'doanh_thu_nam': 8000000000,
            'chi_phi_nam': 4500000000,
            'wacc': 10.5,
            'thue_suat': 20.0
        },
        "🏪 Ví dụ 3: Cửa hàng kinh doanh": {
            'von_dau_tu': 500000000,
            'dong_doi_du_an': 7,
            'doanh_thu_nam': 350000000,
            'chi_phi_nam': 200000000,
            'wacc': 15.0,
            'thue_suat': 20.0
        },
        "💼 Ví dụ 4: Startup công nghệ": {
            'von_dau_tu': 2000000000,
            'dong_doi_du_an': 5,
            'doanh_thu_nam': 1500000000,
            'chi_phi_nam': 900000000,
            'wacc': 18.0,
            'thue_suat': 20.0
        }
    }
    return examples.get(example_name)

# === XỬ LÝ DỮ LIỆU ===

# Check if using example data
if selected_example != "📄 Upload File Word mới":
    example_data = load_example_data(selected_example)
    if example_data and st.session_state.project_data != example_data:
        st.session_state.project_data = example_data
        SessionStateManager.reset_calculation_state()

# Check if API key is available
if not api_key:
    st.warning("⚠️ Vui lòng nhập API Key trong sidebar để sử dụng ứng dụng.")
    st.stop()

# === MAIN WORKFLOW ===

# If upload mode and no file
if selected_example == "📄 Upload File Word mới" and uploaded_file is None:
    st.info("📁 Vui lòng upload file Word trong sidebar để bắt đầu phân tích.")

    # Show sample file format
    with st.expander("📄 Xem định dạng file mẫu"):
        st.markdown("""
        File Word của bạn cần chứa các thông tin sau:

        ```
        Phương án đầu tư [Tên dự án]

        Vốn đầu tư: [số tiền] tỷ đồng
        Thời gian hoạt động: [số năm] năm
        Doanh thu dự kiến: [số tiền] tỷ đồng/năm
        Chi phí vận hành: [số tiền] tỷ đồng/năm
        Chi phí sử dụng vốn (WACC): [số]%
        Thuế suất: 20%
        ```
        """)
    st.stop()

# Extract data from uploaded file
if selected_example == "📄 Upload File Word mới" and uploaded_file is not None:
    # Check if new file
    if st.session_state.uploaded_file_name != uploaded_file.name:
        st.session_state.uploaded_file_name = uploaded_file.name
        SessionStateManager.reset_all_state()

    # Extract button
    st.markdown('<p class="section-header">📄 Bước 1: Trích xuất dữ liệu</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        if st.button("🤖 Trích xuất dữ liệu", type="primary", use_container_width=True):
            with st.spinner("AI đang đọc và phân tích file..."):
                document_text = DocumentReader.extract_text_from_docx(uploaded_file)

                if document_text:
                    ai_service = get_ai_service(api_key)
                    if ai_service:
                        success, data, error_msg = ai_service.extract_project_data(document_text)
                        if success and data:
                            st.session_state.project_data = data
                            SessionStateManager.reset_calculation_state()
                            st.success("✅ Trích xuất thành công!")
                        else:
                            st.error(f"❌ {error_msg}")
                else:
                    st.error("❌ Không thể đọc file")

# === DISPLAY DATA IF AVAILABLE ===
if st.session_state.project_data:

    # Display extracted data
    st.markdown('<p class="section-header">📊 Thông tin dự án</p>', unsafe_allow_html=True)

    p_data = st.session_state.project_data

    # Metrics in columns
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(
            label="💰 Vốn đầu tư",
            value=DataFormatter.format_currency(p_data.get('von_dau_tu', 0))
        )

    with col2:
        st.metric(
            label="⏱️ Thời gian",
            value=f"{p_data.get('dong_doi_du_an', 0)} năm"
        )

    with col3:
        st.metric(
            label="📈 Doanh thu/năm",
            value=DataFormatter.format_currency(p_data.get('doanh_thu_nam', 0))
        )

    with col4:
        st.metric(
            label="💸 Chi phí/năm",
            value=DataFormatter.format_currency(p_data.get('chi_phi_nam', 0))
        )

    with col5:
        st.metric(
            label="📊 WACC",
            value=f"{p_data.get('wacc', 0)}%"
        )

    with col6:
        st.metric(
            label="🏢 Thuế suất",
            value=f"{p_data.get('thue_suat', 0)}%"
        )

    # Edit data option
    with st.expander("✏️ Chỉnh sửa dữ liệu"):
        with st.form("edit_data_form"):
            col1, col2, col3 = st.columns(3)

            with col1:
                von_dau_tu = st.number_input(
                    "Vốn đầu tư (VNĐ)",
                    value=float(p_data.get('von_dau_tu', 0)),
                    min_value=0.0,
                    step=1000000.0
                )
                doanh_thu = st.number_input(
                    "Doanh thu/năm (VNĐ)",
                    value=float(p_data.get('doanh_thu_nam', 0)),
                    min_value=0.0,
                    step=1000000.0
                )

            with col2:
                chi_phi = st.number_input(
                    "Chi phí/năm (VNĐ)",
                    value=float(p_data.get('chi_phi_nam', 0)),
                    min_value=0.0,
                    step=1000000.0
                )
                dong_doi = st.number_input(
                    "Thời gian (năm)",
                    value=int(p_data.get('dong_doi_du_an', 0)),
                    min_value=1,
                    max_value=100,
                    step=1
                )

            with col3:
                wacc = st.number_input(
                    "WACC (%)",
                    value=float(p_data.get('wacc', 0)),
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1
                )
                thue_suat = st.number_input(
                    "Thuế suất (%)",
                    value=float(p_data.get('thue_suat', 0)),
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1
                )

            if st.form_submit_button("💾 Lưu thay đổi", type="primary", use_container_width=True):
                st.session_state.project_data = {
                    'von_dau_tu': von_dau_tu,
                    'dong_doi_du_an': dong_doi,
                    'doanh_thu_nam': doanh_thu,
                    'chi_phi_nam': chi_phi,
                    'wacc': wacc,
                    'thue_suat': thue_suat
                }
                SessionStateManager.reset_calculation_state()
                st.success("✅ Đã lưu thay đổi!")
                st.rerun()

    # === CALCULATE METRICS ===
    if st.session_state.cash_flow_df is None and st.session_state.metrics is None:
        with st.spinner("Đang tính toán các chỉ số tài chính..."):
            df, metrics_data, error_msg = calculate_project_financials(st.session_state.project_data)

            if df is not None and metrics_data is not None:
                st.session_state.cash_flow_df = df
                st.session_state.metrics = metrics_data
            else:
                st.error(f"❌ {error_msg}")

    # === DISPLAY METRICS ===
    if st.session_state.metrics is not None:
        st.markdown('<p class="section-header">📊 Các chỉ số đánh giá</p>', unsafe_allow_html=True)

        m = st.session_state.metrics

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="💎 NPV",
                value=DataFormatter.format_currency(m['NPV']),
                delta="Khả thi" if m['NPV'] > 0 else "Không khả thi",
                delta_color="normal" if m['NPV'] > 0 else "inverse"
            )

        with col2:
            irr_value = DataFormatter.format_percentage(m['IRR']) if isinstance(m['IRR'], float) else m['IRR']
            st.metric(
                label="📈 IRR",
                value=irr_value,
                help="Tỷ suất hoàn vốn nội bộ"
            )

        with col3:
            pp_value = DataFormatter.format_year(m['PP']) if isinstance(m['PP'], float) else m['PP']
            st.metric(
                label="⏱️ PP",
                value=pp_value,
                help="Thời gian hoàn vốn"
            )

        with col4:
            dpp_value = DataFormatter.format_year(m['DPP']) if isinstance(m['DPP'], float) else m['DPP']
            st.metric(
                label="⌛ DPP",
                value=dpp_value,
                help="Thời gian hoàn vốn có chiết khấu"
            )

    # === DISPLAY CASH FLOW TABLE ===
    if st.session_state.cash_flow_df is not None:
        st.markdown('<p class="section-header">💰 Bảng dòng tiền</p>', unsafe_allow_html=True)

        with st.expander("📋 Xem bảng dòng tiền chi tiết", expanded=False):
            st.dataframe(
                st.session_state.cash_flow_df.style.format({
                    'Doanh thu': '{:,.0f}',
                    'Chi phí': '{:,.0f}',
                    'Lợi nhuận trước thuế': '{:,.0f}',
                    'Thuế TNDN': '{:,.0f}',
                    'Lợi nhuận sau thuế': '{:,.0f}',
                    'Dòng tiền thuần (NCF)': '{:,.0f}',
                    'Dòng tiền chiết khấu': '{:,.0f}',
                    'Dòng tiền chiết khấu lũy kế': '{:,.0f}'
                }),
                use_container_width=True,
                height=400
            )

    # === VISUALIZATIONS ===
    if st.session_state.cash_flow_df is not None and st.session_state.metrics is not None:
        st.markdown('<p class="section-header">📊 Phân tích trực quan</p>', unsafe_allow_html=True)

        ProjectVisualizer.render_all_visualizations(
            st.session_state.cash_flow_df,
            st.session_state.metrics,
            st.session_state.project_data
        )

    # === AI ANALYSIS ===
    if st.session_state.metrics is not None:
        st.markdown('<p class="section-header">🤖 Phân tích từ AI</p>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 2, 6])
        with col1:
            if st.button("🧠 Nhận phân tích từ AI", type="primary", use_container_width=True):
                st.session_state.analysis_requested = True

        if st.session_state.analysis_requested:
            if st.session_state.ai_analysis_result is None:
                with st.spinner("AI đang phân tích..."):
                    ai_service = get_ai_service(api_key)
                    if ai_service:
                        success, analysis_text, error_msg = ai_service.analyze_metrics(
                            st.session_state.metrics,
                            st.session_state.project_data
                        )
                        if success:
                            st.session_state.ai_analysis_result = analysis_text
                        else:
                            st.error(f"❌ {error_msg}")

            if st.session_state.ai_analysis_result:
                st.markdown("#### 📝 Nhận định từ chuyên gia AI")
                st.info(st.session_state.ai_analysis_result)

# === FOOTER ===
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #888; font-size: 0.9rem;">💡 Powered by Gemini AI & Streamlit | © 2024</p>',
    unsafe_allow_html=True
)
