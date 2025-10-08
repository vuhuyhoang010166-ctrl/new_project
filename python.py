# -*- coding: utf-8 -*-
"""
Tên ứng dụng: Trình Phân Tích Phương Án Kinh Doanh
Tác giả: Gemini AI (với vai trò chuyên gia Python/Streamlit)
Mô tả: Ứng dụng Streamlit sử dụng AI để trích xuất dữ liệu tài chính từ file Word,
       tính toán các chỉ số hiệu quả dự án (NPV, IRR, PP, DPP) và đưa ra phân tích.

Version: 2.0 - Refactored & Optimized
"""

import streamlit as st
from config import APP_TITLE, APP_ICON, PAGE_LAYOUT, UI_TEXTS
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
    layout=PAGE_LAYOUT
)

# === KHỞI TẠO SESSION STATE ===
SessionStateManager.initialize_session_state()

# === HEADER ===
st.title(f"{APP_ICON} {APP_TITLE} AI")
st.caption("Tải lên phương án kinh doanh dưới dạng file Word (.docx) để AI phân tích và đánh giá.")


# === GIAO DIỆN CHÍNH ===

# Layout: Cột trái (Upload file) và cột phải (API Key)
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader(
        UI_TEXTS["upload_label"],
        type=['docx'],
        help="Chọn file .docx chứa phương án kinh doanh của bạn"
    )

with col2:
    api_key = get_api_key_from_secrets_or_input()


# === XỬ LÝ KHI CÓ FILE VÀ API KEY ===
if uploaded_file is not None and api_key:

    # Kiểm tra nếu file mới được upload (khác file cũ)
    if (st.session_state.uploaded_file_name != uploaded_file.name):
        st.session_state.uploaded_file_name = uploaded_file.name
        SessionStateManager.reset_all_state()

    # === BƯỚC 1: TRÍCH XUẤT DỮ LIỆU ===
    st.markdown("---")
    st.subheader("📄 Bước 1: Trích xuất thông tin bằng AI")

    if st.button(UI_TEXTS["extract_button"], type="primary", use_container_width=True):
        with st.spinner(UI_TEXTS["extract_loading"]):
            # Đọc nội dung file
            document_text = DocumentReader.extract_text_from_docx(uploaded_file)

            if document_text:
                # Khởi tạo AI service
                ai_service = get_ai_service(api_key)

                if ai_service:
                    # Gọi AI để trích xuất dữ liệu
                    success, data, error_msg = ai_service.extract_project_data(document_text)

                    if success and data:
                        st.session_state.project_data = data
                        SessionStateManager.reset_calculation_state()
                    else:
                        st.error(f"❌ Lỗi trích xuất dữ liệu: {error_msg}")
            else:
                st.error("❌ Không thể đọc nội dung file. Vui lòng kiểm tra định dạng file.")

    # === HIỂN THỊ DỮ LIỆU ĐÃ TRÍCH XUẤT ===
    if st.session_state.project_data:
        st.success(UI_TEXTS["extract_success"])

        with st.expander("👁️ Xem dữ liệu AI đã trích xuất", expanded=True):
            p_data = st.session_state.project_data

            # Hiển thị dưới dạng metrics
            metric_col1, metric_col2, metric_col3 = st.columns(3)

            with metric_col1:
                st.metric(
                    label="💰 Vốn đầu tư",
                    value=DataFormatter.format_currency(p_data.get('von_dau_tu', 0))
                )
                st.metric(
                    label="📊 Doanh thu/năm",
                    value=DataFormatter.format_currency(p_data.get('doanh_thu_nam', 0))
                )

            with metric_col2:
                st.metric(
                    label="⏱️ Dòng đời dự án",
                    value=f"{p_data.get('dong_doi_du_an', 0)} năm"
                )
                st.metric(
                    label="💸 Chi phí/năm",
                    value=DataFormatter.format_currency(p_data.get('chi_phi_nam', 0))
                )

            with metric_col3:
                st.metric(
                    label="📈 WACC",
                    value=f"{p_data.get('wacc', 0)}%"
                )
                st.metric(
                    label="🏢 Thuế suất TNDN",
                    value=f"{p_data.get('thue_suat', 0)}%"
                )

            # Cho phép người dùng chỉnh sửa dữ liệu
            if st.checkbox("✏️ Chỉnh sửa dữ liệu (nếu AI trích xuất sai)"):
                with st.form("edit_data_form"):
                    st.markdown("##### Chỉnh sửa thông tin dự án")

                    edit_col1, edit_col2 = st.columns(2)

                    with edit_col1:
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
                        chi_phi = st.number_input(
                            "Chi phí/năm (VNĐ)",
                            value=float(p_data.get('chi_phi_nam', 0)),
                            min_value=0.0,
                            step=1000000.0
                        )

                    with edit_col2:
                        dong_doi = st.number_input(
                            "Dòng đời dự án (năm)",
                            value=int(p_data.get('dong_doi_du_an', 0)),
                            min_value=1,
                            max_value=100,
                            step=1
                        )
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
                        st.success("✅ Đã lưu thay đổi! Vui lòng cuộn xuống để xem kết quả tính toán.")
                        st.rerun()

        # === BƯỚC 2: TÍNH TOÁN CÁC CHỈ SỐ ===
        st.markdown("---")

        # Tự động tính toán khi có dữ liệu
        if st.session_state.cash_flow_df is None and st.session_state.metrics is None:
            with st.spinner(UI_TEXTS["calculate_loading"]):
                df, metrics_data, error_msg = calculate_project_financials(st.session_state.project_data)

                if df is not None and metrics_data is not None:
                    st.session_state.cash_flow_df = df
                    st.session_state.metrics = metrics_data
                else:
                    st.error(f"❌ {error_msg}")

        # === HIỂN THỊ BẢNG DÒNG TIỀN ===
        if st.session_state.cash_flow_df is not None:
            st.subheader("📋 Bước 2: Bảng Dòng Tiền Dự Án")

            # Định dạng hiển thị
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
                use_container_width=True
            )

        # === HIỂN THỊ CÁC CHỈ SỐ ===
        if st.session_state.metrics is not None:
            st.subheader("📊 Bước 3: Các Chỉ Số Đánh Giá Hiệu Quả Dự Án")

            m = st.session_state.metrics
            indicator_cols = st.columns(4)

            with indicator_cols[0]:
                npv_color = "normal" if m['NPV'] >= 0 else "inverse"
                st.metric(
                    label="💎 NPV",
                    value=DataFormatter.format_currency(m['NPV']),
                    help="Giá trị hiện tại ròng - NPV > 0 là tốt"
                )

            with indicator_cols[1]:
                irr_display = (
                    DataFormatter.format_percentage(m['IRR'])
                    if isinstance(m['IRR'], float)
                    else m['IRR']
                )
                st.metric(
                    label="📈 IRR",
                    value=irr_display,
                    help="Tỷ suất hoàn vốn nội bộ - IRR > WACC là tốt"
                )

            with indicator_cols[2]:
                pp_display = (
                    DataFormatter.format_year(m['PP'])
                    if isinstance(m['PP'], float)
                    else m['PP']
                )
                st.metric(
                    label="⏱️ PP",
                    value=pp_display,
                    help="Thời gian hoàn vốn - Càng ngắn càng tốt"
                )

            with indicator_cols[3]:
                dpp_display = (
                    DataFormatter.format_year(m['DPP'])
                    if isinstance(m['DPP'], float)
                    else m['DPP']
                )
                st.metric(
                    label="⌛ DPP",
                    value=dpp_display,
                    help="Thời gian hoàn vốn có chiết khấu"
                )

            # === TRỰC QUAN HÓA ===
            ProjectVisualizer.render_all_visualizations(
                st.session_state.cash_flow_df,
                st.session_state.metrics,
                st.session_state.project_data
            )

            # === BƯỚC 4: PHÂN TÍCH TỪ AI ===
            st.markdown("---")
            st.subheader("🤖 Bước 4: Phân Tích Chuyên Sâu từ AI")

            if st.button(UI_TEXTS["analyze_button"], type="primary", use_container_width=True):
                st.session_state.analysis_requested = True

            if st.session_state.analysis_requested:
                if st.session_state.ai_analysis_result is None:
                    with st.spinner(UI_TEXTS["analyze_loading"]):
                        ai_service = get_ai_service(api_key)

                        if ai_service:
                            success, analysis_text, error_msg = ai_service.analyze_metrics(
                                st.session_state.metrics
                            )

                            if success:
                                st.session_state.ai_analysis_result = analysis_text
                            else:
                                st.error(f"❌ {error_msg}")

                # Hiển thị kết quả phân tích
                if st.session_state.ai_analysis_result:
                    st.markdown("#### 📝 **Nhận định từ Chuyên gia AI**")
                    st.info(st.session_state.ai_analysis_result)

else:
    # Hiển thị thông báo khi chưa có file hoặc API key
    st.info(UI_TEXTS["no_file_warning"])

    # Hiển thị hướng dẫn
    with st.expander("📖 Hướng dẫn sử dụng"):
        st.markdown("""
        ### Cách sử dụng ứng dụng:

        1. **Chuẩn bị file**: Tạo file Word (.docx) chứa thông tin phương án kinh doanh với các thông tin:
           - Vốn đầu tư ban đầu
           - Dòng đời dự án (số năm)
           - Doanh thu hàng năm
           - Chi phí hoạt động hàng năm
           - WACC (tỷ lệ chiết khấu)
           - Thuế suất

        2. **Lấy API Key**: Truy cập [Google AI Studio](https://makersuite.google.com/app/apikey) để lấy API key miễn phí

        3. **Upload file**: Tải file .docx lên ứng dụng

        4. **Nhập API Key**: Dán API key vào ô bên phải (hoặc cấu hình trong secrets)

        5. **Trích xuất**: Nhấn nút "Lọc dữ liệu từ file Word"

        6. **Xem kết quả**: Ứng dụng sẽ tự động:
           - Hiển thị dữ liệu đã trích xuất
           - Tính toán các chỉ số NPV, IRR, PP, DPP
           - Vẽ các biểu đồ trực quan
           - Đưa ra phân tích từ AI

        ### Các chỉ số tài chính:

        - **NPV** (Net Present Value): Giá trị hiện tại ròng - Dự án khả thi khi NPV > 0
        - **IRR** (Internal Rate of Return): Tỷ suất hoàn vốn nội bộ - Dự án tốt khi IRR > WACC
        - **PP** (Payback Period): Thời gian hoàn vốn - Càng ngắn càng tốt
        - **DPP** (Discounted Payback Period): Thời gian hoàn vốn có chiết khấu
        """)


# === FOOTER ===
st.markdown("---")
st.caption("💡 Phát triển bởi AI | Powered by Gemini & Streamlit")
