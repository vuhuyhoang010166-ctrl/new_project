# -*- coding: utf-8 -*-
"""
Module quản lý các API calls tới Gemini AI
"""

import google.generativeai as genai
import streamlit as st
from typing import Dict, Any, Optional, Tuple
from config import (
    GEMINI_MODEL_NAME,
    EXTRACTION_PROMPT_TEMPLATE,
    ANALYSIS_PROMPT_TEMPLATE,
    ERROR_MESSAGES
)
from validators import DataValidator


class GeminiAIService:
    """Class quản lý các tương tác với Gemini AI"""

    def __init__(self, api_key: str):
        """
        Khởi tạo service với API key

        Args:
            api_key: Gemini API key
        """
        self.api_key = api_key
        self.model = None
        self._configure()

    def _configure(self):
        """Cấu hình Gemini AI"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        except Exception as e:
            st.error(f"Lỗi cấu hình API: {e}")
            raise

    @st.cache_data(show_spinner=False, ttl=3600)
    def extract_project_data(_self, text: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Trích xuất dữ liệu dự án từ văn bản sử dụng AI
        Sử dụng cache để tránh gọi API lặp lại với cùng văn bản

        Args:
            text: Văn bản cần phân tích

        Returns:
            Tuple[bool, Optional[Dict], str]: (success, data, error_message)
        """
        if not text or not text.strip():
            return False, None, "Văn bản trống"

        try:
            prompt = EXTRACTION_PROMPT_TEMPLATE.format(text=text)
            response = _self.model.generate_content(prompt)

            if not response or not response.text:
                return False, None, "AI không trả về phản hồi"

            # Validate JSON response
            is_valid, data, error_msg = DataValidator.validate_json_response(response.text)

            if not is_valid:
                return False, None, error_msg

            # Sanitize dữ liệu
            sanitized_data = DataValidator.sanitize_project_data(data)

            return True, sanitized_data, ""

        except Exception as e:
            error_msg = ERROR_MESSAGES["api_error"].format(str(e))
            return False, None, error_msg

    @st.cache_data(show_spinner=False, ttl=3600)
    def analyze_metrics(_self, metrics: Dict[str, Any], project_data: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Phân tích các chỉ số tài chính sử dụng AI
        Sử dụng cache để tránh gọi API lặp lại

        Args:
            metrics: Dictionary chứa các chỉ số tài chính
            project_data: Dictionary chứa thông tin dự án

        Returns:
            Tuple[bool, str, str]: (success, analysis_text, error_message)
        """
        try:
            # Format các giá trị cho prompt - Metrics
            npv = f"{metrics['NPV']:,.0f}"
            irr = f"{metrics['IRR']:.2f}%" if isinstance(metrics['IRR'], float) else metrics['IRR']
            pp = f"{metrics['PP']:.2f} năm" if isinstance(metrics['PP'], float) else metrics['PP']
            dpp = f"{metrics['DPP']:.2f} năm" if isinstance(metrics['DPP'], float) else metrics['DPP']

            # Format các giá trị cho prompt - Project Data
            von_dau_tu = f"{project_data.get('von_dau_tu', 0):,.0f}"
            dong_doi = f"{project_data.get('dong_doi_du_an', 0)}"
            doanh_thu = f"{project_data.get('doanh_thu_nam', 0):,.0f}"
            chi_phi = f"{project_data.get('chi_phi_nam', 0):,.0f}"
            wacc = f"{project_data.get('wacc', 0):.2f}"
            thue_suat = f"{project_data.get('thue_suat', 0):.2f}"

            prompt = ANALYSIS_PROMPT_TEMPLATE.format(
                von_dau_tu=von_dau_tu,
                dong_doi=dong_doi,
                doanh_thu=doanh_thu,
                chi_phi=chi_phi,
                wacc=wacc,
                thue_suat=thue_suat,
                npv=npv,
                irr=irr,
                pp=pp,
                dpp=dpp
            )

            response = _self.model.generate_content(prompt)

            if not response or not response.text:
                return False, "", "AI không trả về phản hồi"

            return True, response.text, ""

        except Exception as e:
            error_msg = ERROR_MESSAGES["api_error"].format(str(e))
            return False, "", error_msg


def get_ai_service(api_key: str) -> Optional[GeminiAIService]:
    """
    Factory function để tạo AI service với validation

    Args:
        api_key: Gemini API key

    Returns:
        GeminiAIService instance hoặc None nếu có lỗi
    """
    # Validate API key
    is_valid, error_msg = DataValidator.validate_api_key(api_key)
    if not is_valid:
        st.error(f"API Key không hợp lệ: {error_msg}")
        return None

    try:
        return GeminiAIService(api_key)
    except Exception as e:
        st.error(f"Không thể khởi tạo AI service: {e}")
        return None
