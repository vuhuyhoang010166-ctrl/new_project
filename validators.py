# -*- coding: utf-8 -*-
"""
Module xác thực và kiểm tra dữ liệu đầu vào
"""

import json
from typing import Dict, Any, Tuple, Optional
from config import DEFAULT_VALUES


class DataValidator:
    """Class để validate dữ liệu từ AI và người dùng"""

    @staticmethod
    def validate_json_response(response_text: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Validate JSON response từ AI

        Returns:
            Tuple[bool, Optional[Dict], str]: (is_valid, data, error_message)
        """
        try:
            # Loại bỏ markdown code blocks
            cleaned = response_text.strip()
            cleaned = cleaned.replace('```json', '').replace('```', '').strip()

            # Parse JSON
            data = json.loads(cleaned)

            # Kiểm tra các trường bắt buộc
            required_fields = [
                'von_dau_tu', 'dong_doi_du_an', 'doanh_thu_nam',
                'chi_phi_nam', 'wacc', 'thue_suat'
            ]

            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return False, None, f"Thiếu các trường: {', '.join(missing_fields)}"

            # Validate data types và giá trị
            is_valid, error_msg = DataValidator.validate_project_data(data)
            if not is_valid:
                return False, None, error_msg

            return True, data, ""

        except json.JSONDecodeError as e:
            return False, None, f"JSON không hợp lệ: {str(e)}"
        except Exception as e:
            return False, None, f"Lỗi không xác định: {str(e)}"

    @staticmethod
    def validate_project_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate dữ liệu dự án

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Kiểm tra vốn đầu tư
            von_dau_tu = float(data.get('von_dau_tu', 0))
            if von_dau_tu < 0:
                return False, "Vốn đầu tư không thể âm"

            # Kiểm tra dòng đời dự án
            dong_doi = int(data.get('dong_doi_du_an', 0))
            if dong_doi <= 0:
                return False, "Dòng đời dự án phải lớn hơn 0"
            if dong_doi > 100:
                return False, "Dòng đời dự án không hợp lý (> 100 năm)"

            # Kiểm tra doanh thu
            doanh_thu = float(data.get('doanh_thu_nam', 0))
            if doanh_thu < 0:
                return False, "Doanh thu không thể âm"

            # Kiểm tra chi phí
            chi_phi = float(data.get('chi_phi_nam', 0))
            if chi_phi < 0:
                return False, "Chi phí không thể âm"

            # Kiểm tra WACC
            wacc = float(data.get('wacc', 0))
            if wacc < 0 or wacc > 100:
                return False, "WACC phải nằm trong khoảng 0-100%"

            # Kiểm tra thuế suất
            thue_suat = float(data.get('thue_suat', 0))
            if thue_suat < 0 or thue_suat > 100:
                return False, "Thuế suất phải nằm trong khoảng 0-100%"

            # Warning nếu dữ liệu không hợp lý
            if von_dau_tu == 0 and doanh_thu == 0:
                return False, "Dữ liệu dự án không đầy đủ (vốn và doanh thu đều bằng 0)"

            return True, ""

        except (ValueError, TypeError) as e:
            return False, f"Lỗi chuyển đổi dữ liệu: {str(e)}"

    @staticmethod
    def sanitize_project_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Làm sạch và chuẩn hóa dữ liệu dự án
        """
        sanitized = {}

        # Convert và làm tròn số
        try:
            sanitized['von_dau_tu'] = max(0, float(data.get('von_dau_tu', 0)))
            sanitized['dong_doi_du_an'] = max(1, int(data.get('dong_doi_du_an', 1)))
            sanitized['doanh_thu_nam'] = max(0, float(data.get('doanh_thu_nam', 0)))
            sanitized['chi_phi_nam'] = max(0, float(data.get('chi_phi_nam', 0)))
            sanitized['wacc'] = max(0, min(100, float(data.get('wacc', 0))))
            sanitized['thue_suat'] = max(0, min(100, float(data.get('thue_suat', 0))))
        except (ValueError, TypeError):
            # Nếu có lỗi, trả về giá trị mặc định
            return DEFAULT_VALUES.copy()

        return sanitized

    @staticmethod
    def validate_api_key(api_key: str) -> Tuple[bool, str]:
        """
        Validate API key format

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not api_key:
            return False, "API Key không được để trống"

        if len(api_key) < 20:
            return False, "API Key có vẻ quá ngắn"

        # Có thể thêm các kiểm tra khác nếu biết format cụ thể

        return True, ""


def get_default_project_data() -> Dict[str, Any]:
    """Trả về dữ liệu mặc định cho dự án"""
    return DEFAULT_VALUES.copy()
