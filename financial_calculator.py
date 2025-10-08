# -*- coding: utf-8 -*-
"""
Module tính toán các chỉ số tài chính dự án
"""

import pandas as pd
import numpy_financial as npf
from typing import Dict, Any, Tuple, Optional
from config import ERROR_MESSAGES


class FinancialCalculator:
    """Class tính toán các chỉ số tài chính cho dự án"""

    def __init__(self, project_data: Dict[str, Any]):
        """
        Khởi tạo calculator với dữ liệu dự án

        Args:
            project_data: Dictionary chứa thông tin dự án
        """
        self.investment = float(project_data['von_dau_tu'])
        self.lifespan = int(project_data['dong_doi_du_an'])
        self.revenue = float(project_data['doanh_thu_nam'])
        self.costs = float(project_data['chi_phi_nam'])
        self.wacc = float(project_data['wacc']) / 100.0
        self.tax_rate = float(project_data['thue_suat']) / 100.0

    def build_cash_flow_table(self) -> pd.DataFrame:
        """
        Xây dựng bảng dòng tiền chi tiết

        Returns:
            DataFrame chứa bảng dòng tiền
        """
        years = list(range(self.lifespan + 1))

        # Khởi tạo các mảng
        profit_before_tax = [0] * (self.lifespan + 1)
        tax = [0] * (self.lifespan + 1)
        profit_after_tax = [0] * (self.lifespan + 1)
        net_cash_flow = [0] * (self.lifespan + 1)

        # Năm 0: Vốn đầu tư
        net_cash_flow[0] = -self.investment

        # Các năm tiếp theo
        for year in range(1, self.lifespan + 1):
            profit_before_tax[year] = self.revenue - self.costs
            tax[year] = profit_before_tax[year] * self.tax_rate if profit_before_tax[year] > 0 else 0
            profit_after_tax[year] = profit_before_tax[year] - tax[year]
            net_cash_flow[year] = profit_after_tax[year]

        # Tạo DataFrame
        cash_flow_df = pd.DataFrame({
            "Năm": years,
            "Doanh thu": [0] + [self.revenue] * self.lifespan,
            "Chi phí": [0] + [self.costs] * self.lifespan,
            "Lợi nhuận trước thuế": profit_before_tax,
            "Thuế TNDN": tax,
            "Lợi nhuận sau thuế": profit_after_tax,
            "Dòng tiền thuần (NCF)": net_cash_flow
        })

        # Tính dòng tiền chiết khấu
        cash_flow_df['Dòng tiền chiết khấu'] = [
            ncf / ((1 + self.wacc) ** year)
            for year, ncf in enumerate(net_cash_flow)
        ]

        # Tính dòng tiền chiết khấu lũy kế
        cash_flow_df['Dòng tiền chiết khấu lũy kế'] = cash_flow_df['Dòng tiền chiết khấu'].cumsum()

        return cash_flow_df

    def calculate_npv(self, net_cash_flow: list) -> float:
        """
        Tính NPV (Net Present Value - Giá trị hiện tại ròng)

        Args:
            net_cash_flow: List các dòng tiền thuần

        Returns:
            Giá trị NPV
        """
        return npf.npv(self.wacc, net_cash_flow)

    def calculate_irr(self, net_cash_flow: list) -> Any:
        """
        Tính IRR (Internal Rate of Return - Tỷ suất hoàn vốn nội bộ)

        Args:
            net_cash_flow: List các dòng tiền thuần

        Returns:
            Giá trị IRR (%) hoặc string "Không thể tính"
        """
        try:
            irr = npf.irr(net_cash_flow)
            if irr is None or pd.isna(irr):
                return "Không thể tính"
            return irr * 100
        except:
            return "Không thể tính"

    def calculate_payback_period(self, cash_flow_df: pd.DataFrame) -> Any:
        """
        Tính PP (Payback Period - Thời gian hoàn vốn)

        Args:
            cash_flow_df: DataFrame bảng dòng tiền

        Returns:
            Thời gian hoàn vốn (năm) hoặc string "Không hoàn vốn"
        """
        try:
            cumulative_cash_flow = cash_flow_df['Dòng tiền thuần (NCF)'].cumsum()

            # Kiểm tra xem có hoàn vốn không
            if cumulative_cash_flow.iloc[-1] < 0:
                return "Không hoàn vốn"

            # Tìm năm cuối cùng còn âm
            negative_years = cumulative_cash_flow[cumulative_cash_flow < 0]
            if len(negative_years) == 0:
                return 0  # Hoàn vốn ngay từ đầu

            last_negative_year = negative_years.index[-1]

            # Số tiền cần bù đắp
            recovery_needed = -cumulative_cash_flow.iloc[last_negative_year]

            # Dòng tiền năm hoàn vốn
            if last_negative_year + 1 >= len(cash_flow_df):
                return "Không hoàn vốn"

            cash_flow_recovery_year = cash_flow_df['Dòng tiền thuần (NCF)'].iloc[last_negative_year + 1]

            if cash_flow_recovery_year <= 0:
                return "Không hoàn vốn"

            pp = last_negative_year + (recovery_needed / cash_flow_recovery_year)
            return pp

        except Exception as e:
            return "Không hoàn vốn"

    def calculate_discounted_payback_period(self, cash_flow_df: pd.DataFrame) -> Any:
        """
        Tính DPP (Discounted Payback Period - Thời gian hoàn vốn có chiết khấu)

        Args:
            cash_flow_df: DataFrame bảng dòng tiền

        Returns:
            Thời gian hoàn vốn có chiết khấu (năm) hoặc string "Không hoàn vốn"
        """
        try:
            cumulative_discounted = cash_flow_df['Dòng tiền chiết khấu lũy kế']

            # Kiểm tra xem có hoàn vốn không
            if cumulative_discounted.iloc[-1] < 0:
                return "Không hoàn vốn"

            # Tìm năm cuối cùng còn âm
            negative_years = cumulative_discounted[cumulative_discounted < 0]
            if len(negative_years) == 0:
                return 0  # Hoàn vốn ngay từ đầu

            last_negative_year = negative_years.index[-1]

            # Số tiền cần bù đắp
            recovery_needed = -cumulative_discounted.iloc[last_negative_year]

            # Dòng tiền chiết khấu năm hoàn vốn
            if last_negative_year + 1 >= len(cash_flow_df):
                return "Không hoàn vốn"

            cash_flow_recovery_year = cash_flow_df['Dòng tiền chiết khấu'].iloc[last_negative_year + 1]

            if cash_flow_recovery_year <= 0:
                return "Không hoàn vốn"

            dpp = last_negative_year + (recovery_needed / cash_flow_recovery_year)
            return dpp

        except Exception as e:
            return "Không hoàn vốn"

    def calculate_all_metrics(self) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]], Optional[str]]:
        """
        Tính toán tất cả các chỉ số tài chính

        Returns:
            Tuple[DataFrame, Dict, str]: (cash_flow_df, metrics, error_message)
        """
        try:
            # Xây dựng bảng dòng tiền
            cash_flow_df = self.build_cash_flow_table()
            net_cash_flow = cash_flow_df['Dòng tiền thuần (NCF)'].tolist()

            # Tính các chỉ số
            npv = self.calculate_npv(net_cash_flow)
            irr = self.calculate_irr(net_cash_flow)
            pp = self.calculate_payback_period(cash_flow_df)
            dpp = self.calculate_discounted_payback_period(cash_flow_df)

            metrics = {
                "NPV": npv,
                "IRR": irr,
                "PP": pp,
                "DPP": dpp
            }

            return cash_flow_df, metrics, None

        except Exception as e:
            error_msg = ERROR_MESSAGES["calculation_error"].format(str(e))
            return None, None, error_msg


def calculate_project_financials(project_data: Dict[str, Any]) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]], Optional[str]]:
    """
    Function tiện ích để tính toán tài chính dự án

    Args:
        project_data: Dictionary chứa dữ liệu dự án

    Returns:
        Tuple[DataFrame, Dict, str]: (cash_flow_df, metrics, error_message)
    """
    try:
        calculator = FinancialCalculator(project_data)
        return calculator.calculate_all_metrics()
    except (TypeError, ValueError, KeyError) as e:
        error_msg = ERROR_MESSAGES["invalid_data"].format(str(e))
        return None, None, error_msg
