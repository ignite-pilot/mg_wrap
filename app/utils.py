"""유틸리티 함수"""
from flask import jsonify, current_app
import traceback

def handle_error(e, user_message="오류가 발생했습니다. 잠시 후 다시 시도해주세요."):
    """
    에러 처리 헬퍼 함수
    - 로그에는 상세 정보 기록
    - 클라이언트에는 일반적인 메시지만 반환
    """
    error_trace = traceback.format_exc()
    current_app.logger.error(f"Error: {str(e)}")
    current_app.logger.error(f"Traceback: {error_trace}")
    return jsonify({'error': 'Internal server error', 'message': user_message}), 500

