from flask import Blueprint, request, jsonify
from app import db
from app.models import DisposalRequest, Asset, StorageApplication, DisposalStatus, AssetStatus
from app.routes.auth import get_current_user
from app.utils import handle_error
from datetime import datetime

disposal_bp = Blueprint('disposal', __name__)

@disposal_bp.route('/request', methods=['POST'])
def request_disposal():
    """폐기 신청"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        asset_id = data.get('asset_id')
        
        if not asset_id:
            return jsonify({'error': 'asset_id is required'}), 400
        
        asset = Asset.query.get_or_404(asset_id)
        application = StorageApplication.query.get(asset.storage_application_id)
        
        if application.user_id != user.get('id'):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # 이미 폐기 신청이 있는지 확인
        existing_request = DisposalRequest.query.filter_by(asset_id=asset_id).first()
        if existing_request and existing_request.status not in [DisposalStatus.CANCELLED, DisposalStatus.COMPLETED]:
            return jsonify({'error': 'Disposal request already exists'}), 400
        
        # 자산 상태 확인
        if asset.status in [AssetStatus.RETRIEVED, AssetStatus.DISPOSED]:
            return jsonify({'error': 'Asset cannot be disposed'}), 400
        
        # 폐기 신청 생성
        if existing_request:
            # 기존 요청 재활성화
            existing_request.status = DisposalStatus.PREPARING
            existing_request.requested_at = datetime.utcnow()
            existing_request.cancelled_at = None
            disposal_request = existing_request
        else:
            disposal_request = DisposalRequest(
                asset_id=asset_id,
                status=DisposalStatus.PREPARING
            )
            db.session.add(disposal_request)
        
        # 자산 상태 업데이트
        asset.status = AssetStatus.DISPOSAL_REQUESTED
        db.session.commit()
        
        return jsonify({
            'success': True,
            'disposal_request': disposal_request.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return handle_error(e, "폐기 신청 처리 중 오류가 발생했습니다.")

@disposal_bp.route('/list', methods=['GET'])
def list_disposals():
    """폐기 현황 목록 조회"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # 사용자의 보관 신청에 속한 자산들의 폐기 신청 조회
        disposal_requests = DisposalRequest.query.join(Asset).join(StorageApplication).filter(
            StorageApplication.user_id == user.get('id')
        ).all()
        
        return jsonify({
            'success': True,
            'disposal_requests': [req.to_dict() for req in disposal_requests]
        }), 200
        
    except Exception as e:
        return handle_error(e, "폐기 신청 처리 중 오류가 발생했습니다.")

@disposal_bp.route('/<int:request_id>/cancel', methods=['POST'])
def cancel_disposal(request_id):
    """폐기 취소 (폐기 준비중인 경우만)"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        disposal_request = DisposalRequest.query.get_or_404(request_id)
        asset = Asset.query.get(disposal_request.asset_id)
        application = StorageApplication.query.get(asset.storage_application_id)
        
        if application.user_id != user.get('id'):
            return jsonify({'error': 'Unauthorized'}), 403
        
        if disposal_request.status != DisposalStatus.PREPARING:
            return jsonify({'error': 'Can only cancel requests in preparing status'}), 400
        
        # 상태 업데이트
        disposal_request.status = DisposalStatus.CANCELLED
        disposal_request.cancelled_at = datetime.utcnow()
        asset.status = AssetStatus.STORED
        db.session.commit()
        
        return jsonify({
            'success': True,
            'disposal_request': disposal_request.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return handle_error(e, "폐기 신청 처리 중 오류가 발생했습니다.")

@disposal_bp.route('/<int:request_id>', methods=['GET'])
def get_disposal(request_id):
    """폐기 신청 상세 조회"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        disposal_request = DisposalRequest.query.get_or_404(request_id)
        asset = Asset.query.get(disposal_request.asset_id)
        application = StorageApplication.query.get(asset.storage_application_id)
        
        if application.user_id != user.get('id'):
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'success': True,
            'disposal_request': disposal_request.to_dict()
        }), 200
        
    except Exception as e:
        return handle_error(e, "폐기 신청 처리 중 오류가 발생했습니다.")

