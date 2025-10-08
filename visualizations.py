# -*- coding: utf-8 -*-
"""
Module chứa tất cả các hàm tạo biểu đồ và visualization
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any


class ProjectVisualizer:
    """Class quản lý các biểu đồ trực quan hóa dự án"""

    @staticmethod
    def create_cash_flow_chart(cash_flow_df: pd.DataFrame) -> go.Figure:
        """Tạo biểu đồ dòng tiền thuần (Cash Flow Waterfall)"""
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=cash_flow_df['Năm'],
            y=cash_flow_df['Dòng tiền thuần (NCF)'],
            name='Dòng tiền thuần',
            marker_color=['red' if x < 0 else 'green' for x in cash_flow_df['Dòng tiền thuần (NCF)']],
            text=[f"{x:,.0f}" for x in cash_flow_df['Dòng tiền thuần (NCF)']],
            textposition='outside'
        ))

        fig.update_layout(
            title="Dòng tiền thuần qua các năm",
            xaxis_title="Năm",
            yaxis_title="VNĐ",
            hovermode='x unified',
            height=400
        )

        return fig

    @staticmethod
    def create_cumulative_cash_flow_chart(cash_flow_df: pd.DataFrame) -> go.Figure:
        """Tạo biểu đồ dòng tiền lũy kế & thời điểm hoàn vốn"""
        cumulative_cf = cash_flow_df['Dòng tiền thuần (NCF)'].cumsum()
        cumulative_discounted = cash_flow_df['Dòng tiền chiết khấu lũy kế']

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=cash_flow_df['Năm'],
            y=cumulative_cf,
            mode='lines+markers',
            name='Dòng tiền lũy kế',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))

        fig.add_trace(go.Scatter(
            x=cash_flow_df['Năm'],
            y=cumulative_discounted,
            mode='lines+markers',
            name='Dòng tiền chiết khấu lũy kế',
            line=dict(color='orange', width=3, dash='dash'),
            marker=dict(size=8)
        ))

        # Đường breakeven (hoàn vốn)
        fig.add_hline(
            y=0,
            line_dash="dot",
            line_color="red",
            annotation_text="Điểm hoàn vốn",
            annotation_position="right"
        )

        fig.update_layout(
            title="Dòng tiền lũy kế - Phân tích hoàn vốn",
            xaxis_title="Năm",
            yaxis_title="VNĐ",
            hovermode='x unified',
            height=400,
            legend=dict(x=0.01, y=0.99)
        )

        return fig

    @staticmethod
    def create_revenue_cost_chart(cash_flow_df: pd.DataFrame) -> go.Figure:
        """Tạo biểu đồ so sánh doanh thu, chi phí & lợi nhuận"""
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=cash_flow_df['Năm'][1:],
            y=cash_flow_df['Doanh thu'][1:],
            name='Doanh thu',
            marker_color='lightblue'
        ))

        fig.add_trace(go.Bar(
            x=cash_flow_df['Năm'][1:],
            y=cash_flow_df['Chi phí'][1:],
            name='Chi phí',
            marker_color='lightcoral'
        ))

        fig.add_trace(go.Scatter(
            x=cash_flow_df['Năm'][1:],
            y=cash_flow_df['Lợi nhuận sau thuế'][1:],
            name='Lợi nhuận sau thuế',
            mode='lines+markers',
            line=dict(color='green', width=3),
            marker=dict(size=10)
        ))

        fig.update_layout(
            title="Phân tích Doanh thu - Chi phí - Lợi nhuận",
            xaxis_title="Năm",
            yaxis_title="VNĐ",
            barmode='group',
            hovermode='x unified',
            height=400
        )

        return fig

    @staticmethod
    def create_npv_gauge(metrics: Dict[str, Any]) -> go.Figure:
        """Tạo biểu đồ NPV (Gauge chart)"""
        npv_value = metrics['NPV']

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=npv_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "NPV (VNĐ)", 'font': {'size': 20}},
            delta={'reference': 0},
            gauge={
                'axis': {'range': [None, npv_value * 1.5 if npv_value > 0 else abs(npv_value) * 0.5]},
                'bar': {'color': "darkgreen" if npv_value > 0 else "red"},
                'steps': [
                    {'range': [0, npv_value * 0.5 if npv_value > 0 else 0], 'color': "lightgray"},
                    {'range': [npv_value * 0.5 if npv_value > 0 else 0, npv_value if npv_value > 0 else 0], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0
                }
            }
        ))

        fig.update_layout(height=300)
        return fig

    @staticmethod
    def create_irr_wacc_comparison(metrics: Dict[str, Any], project_data: Dict[str, Any]) -> go.Figure:
        """Tạo biểu đồ so sánh IRR vs WACC"""
        if not isinstance(metrics['IRR'], float):
            # Nếu IRR không tính được, trả về figure trống với thông báo
            fig = go.Figure()
            fig.add_annotation(
                text="IRR không thể tính toán",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(height=300)
            return fig

        wacc = float(project_data.get('wacc', 0))
        irr = metrics['IRR']

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=['WACC', 'IRR'],
            y=[wacc, irr],
            marker_color=['orange', 'green' if irr > wacc else 'red'],
            text=[f"{wacc:.2f}%", f"{irr:.2f}%"],
            textposition='outside'
        ))

        fig.update_layout(
            title="So sánh IRR với WACC",
            yaxis_title="Tỷ lệ (%)",
            showlegend=False,
            height=300
        )

        return fig

    @staticmethod
    def create_financial_structure_pie(project_data: Dict[str, Any]) -> go.Figure:
        """Tạo biểu đồ phân bổ vốn (Pie chart)"""
        investment = float(project_data.get('von_dau_tu', 0))
        total_revenue = float(project_data.get('doanh_thu_nam', 0)) * int(project_data.get('dong_doi_du_an', 0))
        total_costs = float(project_data.get('chi_phi_nam', 0)) * int(project_data.get('dong_doi_du_an', 0))
        profit = total_revenue - total_costs - investment

        fig = go.Figure(data=[go.Pie(
            labels=['Vốn đầu tư ban đầu', 'Tổng chi phí vận hành', 'Lợi nhuận dự kiến'],
            values=[investment, total_costs, profit if profit > 0 else 0],
            hole=0.4,
            marker_colors=['#ff9999', '#ffcc99', '#99ff99']
        )])

        fig.update_layout(
            title="Phân bổ nguồn vốn và lợi nhuận dự án",
            height=400,
            annotations=[dict(
                text='Cấu trúc<br>Tài chính',
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False
            )]
        )

        return fig

    @staticmethod
    def render_all_visualizations(cash_flow_df: pd.DataFrame, metrics: Dict[str, Any], project_data: Dict[str, Any]):
        """Render tất cả các biểu đồ"""

        st.markdown("---")
        st.subheader("📊 Trực Quan Hóa Dữ Liệu Dự Án")

        # 1. Biểu đồ dòng tiền thuần
        st.markdown("#### 📊 Biểu đồ Dòng Tiền Thuần theo Năm")
        fig_cashflow = ProjectVisualizer.create_cash_flow_chart(cash_flow_df)
        st.plotly_chart(fig_cashflow, use_container_width=True)

        # 2. Biểu đồ dòng tiền lũy kế
        st.markdown("#### 💰 Biểu đồ Dòng Tiền Lũy Kế & Thời Điểm Hoàn Vốn")
        fig_cumulative = ProjectVisualizer.create_cumulative_cash_flow_chart(cash_flow_df)
        st.plotly_chart(fig_cumulative, use_container_width=True)

        # 3. So sánh doanh thu & chi phí
        st.markdown("#### 📈 So Sánh Doanh Thu, Chi Phí & Lợi Nhuận")
        fig_revenue = ProjectVisualizer.create_revenue_cost_chart(cash_flow_df)
        st.plotly_chart(fig_revenue, use_container_width=True)

        # 4. Dashboard chỉ số tài chính
        st.markdown("#### 🎯 Dashboard Chỉ Số Tài Chính")
        col1, col2 = st.columns(2)

        with col1:
            fig_npv = ProjectVisualizer.create_npv_gauge(metrics)
            st.plotly_chart(fig_npv, use_container_width=True)

        with col2:
            fig_irr = ProjectVisualizer.create_irr_wacc_comparison(metrics, project_data)
            st.plotly_chart(fig_irr, use_container_width=True)

        # 5. Cấu trúc tài chính
        st.markdown("#### 💼 Cấu Trúc Tài Chính Dự Án")
        fig_structure = ProjectVisualizer.create_financial_structure_pie(project_data)
        st.plotly_chart(fig_structure, use_container_width=True)
