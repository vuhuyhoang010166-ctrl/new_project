# -*- coding: utf-8 -*-
"""
Tên ứng dụng: Trình Phân Tích Phương Án Kinh Doanh
Tác giả: Gemini AI (với vai trò chuyên gia Python/Streamlit)
Mô tả: Ứng dụng Streamlit sử dụng AI để trích xuất dữ liệu tài chính từ file Word,
       tính toán các chỉ số hiệu quả dự án (NPV, IRR, PP, DPP) và đưa ra phân tích.
"""

import streamlit as st
import pandas as pd
import numpy_financial as npf
import google.generativeai as genai
from docx import Document
import json
import io
import plotly.graph_objects as go
import plotly.express as px

# --- Cấu hình Trang và Tiêu đề ---
st.set_page_config(
    page_title="Trình Phân Tích Phương Án Kinh Doanh",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Trình Phân Tích Phương Án Kinh Doanh AI")
st.caption("Tải lên phương án kinh doanh dưới dạng file Word (.docx) để AI phân tích và đánh giá.")

# --- KHỞI TẠO BIẾN TRẠNG THÁI (SESSION STATE) ---
# Rất quan trọng để lưu trữ dữ liệu giữa các lần chạy lại của script
if 'project_data' not in st.session_state:
    st.session_state.project_data = None
if 'cash_flow_df' not in st.session_state:
    st.session_state.cash_flow_df = None
if 'metrics' not in st.session_state:
    st.session_state.metrics = None
if 'analysis_requested' not in st.session_state:
    st.session_state.analysis_requested = False


# --- HÀM HỖ TRỢ ---

def extract_text_from_docx(uploaded_file):
    """Đọc và trích xuất toàn bộ văn bản từ file .docx."""
    # Sử dụng BytesIO để đọc file từ bộ nhớ mà không cần lưu xuống đĩa
    document = Document(io.BytesIO(uploaded_file.read()))
    full_text = [para.text for para in document.paragraphs]
    return '\n'.join(full_text)

def get_project_data_from_ai(text, api_key):
    """
    Sử dụng Gemini AI để trích xuất các thông số tài chính từ văn bản.
    Trả về một dictionary Python.
    """
    try:
        genai.configure(api_key=api_key)
        # *** ĐÃ SỬA: Sử dụng model name chính xác với version cụ thể ***
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Prompt được thiết kế kỹ lưỡng để yêu cầu AI trả về định dạng JSON,
        # giúp việc xử lý dữ liệu trở nên đáng tin cậy hơn.
        prompt = f"""
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
        response = model.generate_content(prompt)
        # Loại bỏ các ký tự không cần thiết mà AI có thể thêm vào
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_response)

    except Exception as e:
        st.error(f"Lỗi khi gọi API của AI: {e}")
        st.error(f"Phản hồi nhận được từ AI: {response.text if 'response' in locals() else 'Không có phản hồi'}")
        return None

@st.cache_data
def calculate_financials(project_data):
    """
    Xây dựng bảng dòng tiền và tính toán các chỉ số tài chính.
    Sử dụng @st.cache_data để không phải tính toán lại nếu đầu vào không đổi.
    """
    try:
        # Lấy dữ liệu và chuyển đổi sang đúng định dạng
        investment = float(project_data['von_dau_tu'])
        lifespan = int(project_data['dong_doi_du_an'])
        revenue = float(project_data['doanh_thu_nam'])
        costs = float(project_data['chi_phi_nam'])
        wacc = float(project_data['wacc']) / 100.0
        tax_rate = float(project_data['thue_suat']) / 100.0

        # --- Xây dựng bảng dòng tiền ---
        years = list(range(lifespan + 1))
        profit_before_tax = [0] * (lifespan + 1)
        tax = [0] * (lifespan + 1)
        profit_after_tax = [0] * (lifespan + 1)
        net_cash_flow = [0] * (lifespan + 1)

        net_cash_flow[0] = -investment  # Dòng tiền năm 0 là vốn đầu tư

        for year in range(1, lifespan + 1):
            profit_before_tax[year] = revenue - costs
            tax[year] = profit_before_tax[year] * tax_rate if profit_before_tax[year] > 0 else 0
            profit_after_tax[year] = profit_before_tax[year] - tax[year]
            # Giả định đơn giản: Dòng tiền thuần = Lợi nhuận sau thuế
            # (Trong thực tế có thể cộng lại khấu hao)
            net_cash_flow[year] = profit_after_tax[year]

        cash_flow_df = pd.DataFrame({
            "Năm": years,
            "Doanh thu": [0] + [revenue] * lifespan,
            "Chi phí": [0] + [costs] * lifespan,
            "Lợi nhuận trước thuế": profit_before_tax,
            "Thuế TNDN": tax,
            "Lợi nhuận sau thuế": profit_after_tax,
            "Dòng tiền thuần (NCF)": net_cash_flow
        })

        # --- Tính toán các chỉ số ---
        # NPV (Giá trị hiện tại ròng)
        npv = npf.npv(wacc, net_cash_flow)

        # IRR (Tỷ suất hoàn vốn nội bộ)
        try:
            irr = npf.irr(net_cash_flow) * 100
        except:
            irr = "Không thể tính" # Xảy ra khi dòng tiền không đổi dấu

        # PP (Thời gian hoàn vốn)
        cumulative_cash_flow = cash_flow_df['Dòng tiền thuần (NCF)'].cumsum()
        try:
            # Năm trước khi hoàn vốn
            last_negative_year = cumulative_cash_flow[cumulative_cash_flow < 0].idxmax()
            # Số tiền cần bù đắp ở năm hoàn vốn
            recovery_needed = -cumulative_cash_flow.iloc[last_negative_year]
            # Dòng tiền của năm hoàn vốn
            cash_flow_recovery_year = cash_flow_df['Dòng tiền thuần (NCF)'].iloc[last_negative_year + 1]
            pp = last_negative_year + (recovery_needed / cash_flow_recovery_year)
        except:
            pp = "Không hoàn vốn"

        # DPP (Thời gian hoàn vốn có chiết khấu)
        cash_flow_df['Dòng tiền chiết khấu'] = [ncf / ((1 + wacc)**year) for year, ncf in enumerate(net_cash_flow)]
        cash_flow_df['Dòng tiền chiết khấu lũy kế'] = cash_flow_df['Dòng tiền chiết khấu'].cumsum()
        try:
            last_negative_year_d = cash_flow_df['Dòng tiền chiết khấu lũy kế'][cash_flow_df['Dòng tiền chiết khấu lũy kế'] < 0].idxmax()
            recovery_needed_d = -cash_flow_df['Dòng tiền chiết khấu lũy kế'].iloc[last_negative_year_d]
            cash_flow_recovery_year_d = cash_flow_df['Dòng tiền chiết khấu'].iloc[last_negative_year_d + 1]
            dpp = last_negative_year_d + (recovery_needed_d / cash_flow_recovery_year_d)
        except:
            dpp = "Không hoàn vốn"

        metrics = {
            "NPV": npv,
            "IRR": irr,
            "PP": pp,
            "DPP": dpp
        }

        return cash_flow_df, metrics
    except (TypeError, ValueError, KeyError) as e:
        st.error(f"Dữ liệu đầu vào không hợp lệ để tính toán. Vui lòng kiểm tra lại thông tin AI đã trích xuất. Lỗi: {e}")
        return None, None

def get_ai_analysis(metrics, api_key):
    """Gửi các chỉ số đã tính toán để AI đưa ra phân tích chuyên sâu."""
    try:
        genai.configure(api_key=api_key)
        # *** ĐÃ SỬA: Sử dụng model name chính xác với version cụ thể ***
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""
        Với vai trò là một chuyên gia tư vấn đầu tư, hãy phân tích các chỉ số hiệu quả dự án dưới đây và đưa ra nhận định chuyên môn.
        Giải thích ngắn gọn ý nghĩa của từng chỉ số trong bối cảnh của dự án này.
        Cuối cùng, đưa ra một kết luận tổng quan về tính khả thi của dự án (ví dụ: rất khả thi, cần cân nhắc, rủi ro cao...).

        Các chỉ số cần phân tích:
        - Giá trị hiện tại ròng (NPV): {metrics['NPV']:,.0f} VNĐ
        - Tỷ suất hoàn vốn nội bộ (IRR): {f"{metrics['IRR']:.2f}%" if isinstance(metrics['IRR'], float) else metrics['IRR']}
        - Thời gian hoàn vốn (PP): {f"{metrics['PP']:.2f} năm" if isinstance(metrics['PP'], float) else metrics['PP']}
        - Thời gian hoàn vốn có chiết khấu (DPP): {f"{metrics['DPP']:.2f} năm" if isinstance(metrics['DPP'], float) else metrics['DPP']}

        Hãy trình bày câu trả lời một cách chuyên nghiệp, có cấu trúc rõ ràng với các đề mục cho từng phần.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Lỗi khi gọi API của AI để phân tích: {e}")
        return "Không thể nhận được phân tích từ AI."

def create_visualizations(cash_flow_df, metrics, project_data):
    """Tạo các biểu đồ trực quan hóa dữ liệu dự án."""
    
    # 1. BIỂU ĐỒ DÒNG TIỀN THUẦN (Cash Flow Waterfall)
    st.markdown("#### 📊 Biểu đồ Dòng Tiền Thuần theo Năm")
    fig_cashflow = go.Figure()
    
    fig_cashflow.add_trace(go.Bar(
        x=cash_flow_df['Năm'],
        y=cash_flow_df['Dòng tiền thuần (NCF)'],
        name='Dòng tiền thuần',
        marker_color=['red' if x < 0 else 'green' for x in cash_flow_df['Dòng tiền thuần (NCF)']],
        text=[f"{x:,.0f}" for x in cash_flow_df['Dòng tiền thuần (NCF)']],
        textposition='outside'
    ))
    
    fig_cashflow.update_layout(
        title="Dòng tiền thuần qua các năm",
        xaxis_title="Năm",
        yaxis_title="VNĐ",
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig_cashflow, use_container_width=True)
    
    # 2. BIỂU ĐỒ DÒNG TIỀN LŨY KẾ (Cumulative Cash Flow)
    st.markdown("#### 💰 Biểu đồ Dòng Tiền Lũy Kế & Thời Điểm Hoàn Vốn")
    
    cumulative_cf = cash_flow_df['Dòng tiền thuần (NCF)'].cumsum()
    cumulative_discounted = cash_flow_df['Dòng tiền chiết khấu lũy kế']
    
    fig_cumulative = go.Figure()
    
    fig_cumulative.add_trace(go.Scatter(
        x=cash_flow_df['Năm'],
        y=cumulative_cf,
        mode='lines+markers',
        name='Dòng tiền lũy kế',
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ))
    
    fig_cumulative.add_trace(go.Scatter(
        x=cash_flow_df['Năm'],
        y=cumulative_discounted,
        mode='lines+markers',
        name='Dòng tiền chiết khấu lũy kế',
        line=dict(color='orange', width=3, dash='dash'),
        marker=dict(size=8)
    ))
    
    # Đường breakeven (hoàn vốn)
    fig_cumulative.add_hline(y=0, line_dash="dot", line_color="red", 
                             annotation_text="Điểm hoàn vốn", 
                             annotation_position="right")
    
    fig_cumulative.update_layout(
        title="Dòng tiền lũy kế - Phân tích hoàn vốn",
        xaxis_title="Năm",
        yaxis_title="VNĐ",
        hovermode='x unified',
        height=400,
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig_cumulative, use_container_width=True)
    
    # 3. BIỂU ĐỒ SO SÁNH DOANH THU & CHI PHÍ
    st.markdown("#### 📈 So Sánh Doanh Thu, Chi Phí & Lợi Nhuận")
    
    fig_revenue = go.Figure()
    
    fig_revenue.add_trace(go.Bar(
        x=cash_flow_df['Năm'][1:],  # Bỏ năm 0
        y=cash_flow_df['Doanh thu'][1:],
        name='Doanh thu',
        marker_color='lightblue'
    ))
    
    fig_revenue.add_trace(go.Bar(
        x=cash_flow_df['Năm'][1:],
        y=cash_flow_df['Chi phí'][1:],
        name='Chi phí',
        marker_color='lightcoral'
    ))
    
    fig_revenue.add_trace(go.Scatter(
        x=cash_flow_df['Năm'][1:],
        y=cash_flow_df['Lợi nhuận sau thuế'][1:],
        name='Lợi nhuận sau thuế',
        mode='lines+markers',
        line=dict(color='green', width=3),
        marker=dict(size=10)
    ))
    
    fig_revenue.update_layout(
        title="Phân tích Doanh thu - Chi phí - Lợi nhuận",
        xaxis_title="Năm",
        yaxis_title="VNĐ",
        barmode='group',
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig_revenue, use_container_width=True)
    
    # 4. BIỂU ĐỒ TÀI CHÍNH CHỦ CHỐT (Dashboard)
    st.markdown("#### 🎯 Dashboard Chỉ Số Tài Chính")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Biểu đồ NPV
        fig_npv = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=metrics['NPV'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "NPV (VNĐ)", 'font': {'size': 20}},
            delta={'reference': 0},
            gauge={
                'axis': {'range': [None, metrics['NPV'] * 1.5]},
                'bar': {'color': "darkgreen" if metrics['NPV'] > 0 else "red"},
                'steps': [
                    {'range': [0, metrics['NPV'] * 0.5], 'color': "lightgray"},
                    {'range': [metrics['NPV'] * 0.5, metrics['NPV']], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0
                }
            }
        ))
        fig_npv.update_layout(height=300)
        st.plotly_chart(fig_npv, use_container_width=True)
    
    with col2:
        # Biểu đồ IRR vs WACC
        if isinstance(metrics['IRR'], float):
            wacc = float(project_data.get('wacc', 0))
            
            fig_irr = go.Figure()
            
            fig_irr.add_trace(go.Bar(
                x=['WACC', 'IRR'],
                y=[wacc, metrics['IRR']],
                marker_color=['orange', 'green' if metrics['IRR'] > wacc else 'red'],
                text=[f"{wacc:.2f}%", f"{metrics['IRR']:.2f}%"],
                textposition='outside'
            ))
            
            fig_irr.update_layout(
                title="So sánh IRR với WACC",
                yaxis_title="Tỷ lệ (%)",
                showlegend=False,
                height=300
            )
            st.plotly_chart(fig_irr, use_container_width=True)
    
    # 5. BIỂU ĐỒ PHÂN BỔ VỐN
    st.markdown("#### 💼 Cấu Trúc Tài Chính Dự Án")
    
    investment = float(project_data.get('von_dau_tu', 0))
    total_revenue = float(project_data.get('doanh_thu_nam', 0)) * int(project_data.get('dong_doi_du_an', 0))
    total_costs = float(project_data.get('chi_phi_nam', 0)) * int(project_data.get('dong_doi_du_an', 0))
    
    fig_structure = go.Figure(data=[go.Pie(
        labels=['Vốn đầu tư ban đầu', 'Tổng chi phí vận hành', 'Lợi nhuận dự kiến'],
        values=[investment, total_costs, total_revenue - total_costs - investment],
        hole=0.4,
        marker_colors=['#ff9999', '#ffcc99', '#99ff99']
    )])
    
    fig_structure.update_layout(
        title="Phân bổ nguồn vốn và lợi nhuận dự án",
        height=400,
        annotations=[dict(text='Cấu trúc<br>Tài chính', x=0.5, y=0.5, font_size=16, showarrow=False)]
    )
    st.plotly_chart(fig_structure, use_container_width=True)

# --- GIAO DIỆN NGƯỜI DÙNG ---

# Cột bên trái cho việc nhập liệu, cột bên phải cho API Key
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader(
        "1. Tải lên file phương án kinh doanh (.docx)",
        type=['docx']
    )

with col2:
    # Lấy API Key từ Streamlit Secrets
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("Đã tìm thấy API Key.", icon="🔑")
    except:
        api_key = st.text_input("Hoặc nhập Gemini API Key của bạn vào đây:", type="password")


if uploaded_file is not None and api_key:
    # --- BƯỚC 1: TRÍCH XUẤT DỮ LIỆU ---
    st.markdown("---")
    st.subheader("Bước 1: Trích xuất thông tin bằng AI")

    if st.button("Lọc dữ liệu từ file Word", type="primary"):
        with st.spinner("AI đang đọc và phân tích file... Vui lòng chờ trong giây lát..."):
            # Trích xuất văn bản từ file
            document_text = extract_text_from_docx(uploaded_file)
            # Gọi AI để lấy dữ liệu có cấu trúc
            st.session_state.project_data = get_project_data_from_ai(document_text, api_key)
            # Đặt lại các kết quả cũ
            st.session_state.cash_flow_df = None
            st.session_state.metrics = None
            st.session_state.analysis_requested = False


    if st.session_state.project_data:
        st.success("✅ AI đã trích xuất thành công dữ liệu!")
        with st.expander("Xem dữ liệu AI đã lọc", expanded=True):
            # Hiển thị dữ liệu đã trích xuất dưới dạng các metric để dễ nhìn hơn
            p_data = st.session_state.project_data
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric(label="Vốn đầu tư", value=f"{p_data.get('von_dau_tu', 0):,.0f} VNĐ")
                st.metric(label="Doanh thu/năm", value=f"{p_data.get('doanh_thu_nam', 0):,.0f} VNĐ")
            with metric_col2:
                st.metric(label="Dòng đời dự án", value=f"{p_data.get('dong_doi_du_an', 0)} năm")
                st.metric(label="Chi phí/năm", value=f"{p_data.get('chi_phi_nam', 0):,.0f} VNĐ")
            with metric_col3:
                st.metric(label="WACC", value=f"{p_data.get('wacc', 0)} %")
                st.metric(label="Thuế suất TNDN", value=f"{p_data.get('thue_suat', 0)} %")

        # --- BƯỚC 2 & 3: TÍNH TOÁN VÀ HIỂN THỊ KẾT QUẢ ---
        st.markdown("---")
        # Thực hiện tính toán ngay sau khi có dữ liệu
        if st.session_state.cash_flow_df is None and st.session_state.metrics is None:
            with st.spinner("Đang xây dựng bảng dòng tiền và tính toán các chỉ số..."):
                df, metrics_data = calculate_financials(st.session_state.project_data)
                if df is not None and metrics_data is not None:
                    st.session_state.cash_flow_df = df
                    st.session_state.metrics = metrics_data

        if st.session_state.cash_flow_df is not None:
            st.subheader("Bước 2: Bảng Dòng Tiền Dự Án")
            # Định dạng các cột số cho dễ đọc
            st.dataframe(st.session_state.cash_flow_df.style.format({
                'Doanh thu': '{:,.0f}',
                'Chi phí': '{:,.0f}',
                'Lợi nhuận trước thuế': '{:,.0f}',
                'Thuế TNDN': '{:,.0f}',
                'Lợi nhuận sau thuế': '{:,.0f}',
                'Dòng tiền thuần (NCF)': '{:,.0f}',
                'Dòng tiền chiết khấu': '{:,.0f}',
                'Dòng tiền chiết khấu lũy kế': '{:,.0f}'
            }), use_container_width=True)

        if st.session_state.metrics is not None:
            st.subheader("Bước 3: Các Chỉ Số Đánh Giá Hiệu Quả Dự Án")
            m = st.session_state.metrics
            indicator_cols = st.columns(4)
            with indicator_cols[0]:
                st.metric(label="Giá trị hiện tại ròng (NPV)", value=f"{m['NPV']:,.0f} VNĐ")
            with indicator_cols[1]:
                st.metric(label="Tỷ suất hoàn vốn nội bộ (IRR)", value=f"{m['IRR']:.2f} %" if isinstance(m['IRR'], float) else m['IRR'])
            with indicator_cols[2]:
                st.metric(label="Thời gian hoàn vốn (PP)", value=f"{m['PP']:.2f} năm" if isinstance(m['PP'], float) else m['PP'])
            with indicator_cols[3]:
                st.metric(label="Thời gian hoàn vốn có chiết khấu (DPP)", value=f"{m['DPP']:.2f} năm" if isinstance(m['DPP'], float) else m['DPP'])

            # --- TRỰC QUAN HÓA DỮ LIỆU ---
            st.markdown("---")
            st.subheader("📊 Trực Quan Hóa Dữ Liệu Dự Án")
            create_visualizations(st.session_state.cash_flow_df, st.session_state.metrics, st.session_state.project_data)

            # --- BƯỚC 4: PHÂN TÍCH TỪ AI ---
            st.markdown("---")
            st.subheader("Bước 4: Yêu cầu AI Phân Tích Chuyên Sâu")
            if st.button("Phân tích các chỉ số hiệu quả", type="primary"):
                st.session_state.analysis_requested = True

            if st.session_state.analysis_requested:
                with st.spinner("AI đang soạn thảo phân tích chuyên môn..."):
                    analysis_result = get_ai_analysis(st.session_state.metrics, api_key)
                    st.markdown("#### 📝 **Nhận định từ Chuyên gia AI**")
                    st.info(analysis_result)
else:
    st.info("Vui lòng tải lên file .docx và đảm bảo đã cung cấp API Key để bắt đầu.")
