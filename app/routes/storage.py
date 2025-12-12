from flask import Blueprint, request, jsonify
from app import db
from app.models import StorageApplication, StorageType, ApplicationStatus
from app.routes.auth import get_current_user
from app.utils import handle_error

storage_bp = Blueprint('storage', __name__)

# 가격 정책
PRICING = {
    'space': {
        1: 300000,  # 5평 기준 1개월
        3: 800000,  # 5평 기준 3개월
        6: 1500000  # 5평 기준 6개월
    },
    'box': {
        1: 30000,   # BOX 1개 기준 1개월
        3: 80000,   # BOX 1개 기준 3개월
        6: 150000   # BOX 1개 기준 6개월
    }
}

def calculate_price(storage_type, months, space_pyeong=None, box_count=None):
    """견적 금액 계산"""
    base_price = PRICING[storage_type].get(months, 0)
    
    if storage_type == 'space':
        # 공간형: 5평 기준으로 계산, 평수에 비례
        if space_pyeong:
            multiplier = space_pyeong / 5.0
            return int(base_price * multiplier)
    elif storage_type == 'box':
        # BOX형: BOX 수량에 비례
        if box_count:
            return int(base_price * box_count)
    
    return base_price

@storage_bp.route('/estimate', methods=['POST'])
def get_estimate():
    """견적 금액 조회"""
    try:
        data = request.get_json()
        storage_type = data.get('storage_type')  # 'space' or 'box'
        months = data.get('months')
        space_pyeong = data.get('space_pyeong')
        box_count = data.get('box_count')
        
        if not storage_type or not months:
            return jsonify({'error': 'storage_type and months are required'}), 400
        
        if storage_type == 'space' and not space_pyeong:
            return jsonify({'error': 'space_pyeong is required for space type'}), 400
        
        if storage_type == 'box' and not box_count:
            return jsonify({'error': 'box_count is required for box type'}), 400
        
        if months not in [1, 3, 6]:
            return jsonify({'error': 'months must be 1, 3, or 6'}), 400
        
        estimated_price = calculate_price(storage_type, months, space_pyeong, box_count)
        
        return jsonify({
            'success': True,
            'estimated_price': estimated_price,
            'storage_type': storage_type,
            'months': months,
            'space_pyeong': space_pyeong,
            'box_count': box_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@storage_bp.route('/apply', methods=['POST'])
def apply_storage():
    """보관 신청"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        storage_type = data.get('storage_type')
        months = data.get('months')
        space_pyeong = data.get('space_pyeong')
        box_count = data.get('box_count')
        
        if not storage_type or not months:
            return jsonify({'error': 'storage_type and months are required'}), 400
        
        if storage_type == 'space' and not space_pyeong:
            return jsonify({'error': 'space_pyeong is required for space type'}), 400
        
        if storage_type == 'box' and not box_count:
            return jsonify({'error': 'box_count is required for box type'}), 400
        
        if months not in [1, 3, 6]:
            return jsonify({'error': 'months must be 1, 3, or 6'}), 400
        
        estimated_price = calculate_price(storage_type, months, space_pyeong, box_count)
        
        # 보관 신청 생성
        application = StorageApplication(
            user_id=user.get('id'),
            storage_type=StorageType.SPACE if storage_type == 'space' else StorageType.BOX,
            space_pyeong=space_pyeong,
            box_count=box_count,
            months=months,
            estimated_price=estimated_price,
            status=ApplicationStatus.APPROVED  # 자동 승인
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'application': application.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return handle_error(e, "보관 신청 처리 중 오류가 발생했습니다.")

@storage_bp.route('/list', methods=['GET'])
def list_applications():
    """보관 신청 목록 조회"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        applications = StorageApplication.query.filter_by(user_id=user.get('id')).all()
        
        return jsonify({
            'success': True,
            'applications': [app.to_dict() for app in applications]
        }), 200
        
    except Exception as e:
        return handle_error(e, "보관 신청 목록 조회 중 오류가 발생했습니다.")

@storage_bp.route('/<int:application_id>', methods=['GET'])
def get_application(application_id):
    """보관 신청 상세 조회"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        application = StorageApplication.query.get_or_404(application_id)
        
        if application.user_id != user.get('id'):
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'success': True,
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

