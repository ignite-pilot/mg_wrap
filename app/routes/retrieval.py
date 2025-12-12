from flask import Blueprint, request, jsonify
from app import db
from app.models import RetrievalRequest, Asset, StorageApplication, RetrievalStatus, AssetStatus
from app.routes.auth import get_current_user
from app.utils import handle_error
from datetime import datetime

retrieval_bp = Blueprint('retrieval', __name__)

@retrieval_bp.route('/request', methods=['POST'])
def request_retrieval():
    """회수 신청"""
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
        
        # 이미 회수 신청이 있는지 확인
        existing_request = RetrievalRequest.query.filter_by(asset_id=asset_id).first()
        if existing_request and existing_request.status not in [RetrievalStatus.CANCELLED, RetrievalStatus.COMPLETED]:
            return jsonify({'error': 'Retrieval request already exists'}), 400
        
        # 자산 상태 확인
        if asset.status in [AssetStatus.RETRIEVED, AssetStatus.DISPOSED]:
            return jsonify({'error': 'Asset cannot be retrieved'}), 400
        
        # 회수 신청 생성
        if existing_request:
            # 기존 요청 재활성화
            existing_request.status = RetrievalStatus.PREPARING
            existing_request.requested_at = datetime.utcnow()
            existing_request.cancelled_at = None
            retrieval_request = existing_request
        else:
            retrieval_request = RetrievalRequest(
                asset_id=asset_id,
                status=RetrievalStatus.PREPARING
            )
            db.session.add(retrieval_request)
        
        # 자산 상태 업데이트
        asset.status = AssetStatus.RETRIEVAL_REQUESTED
        db.session.commit()
        
        return jsonify({
            'success': True,
            'retrieval_request': retrieval_request.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return handle_error(e, "회수 신청 처리 중 오류가 발생했습니다.")

@retrieval_bp.route('/list', methods=['GET'])
def list_retrievals():
    """회수 현황 목록 조회"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # 사용자의 보관 신청에 속한 자산들의 회수 신청 조회
        retrieval_requests = RetrievalRequest.query.join(Asset).join(StorageApplication).filter(
            StorageApplication.user_id == user.get('id')
        ).all()
        
        return jsonify({
            'success': True,
            'retrieval_requests': [req.to_dict() for req in retrieval_requests]
        }), 200
        
    except Exception as e:
        return handle_error(e, "회수 신청 처리 중 오류가 발생했습니다.")

@retrieval_bp.route('/<int:request_id>/cancel', methods=['POST'])
def cancel_retrieval(request_id):
    """회수 취소 (출고 준비중인 경우만)"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        retrieval_request = RetrievalRequest.query.get_or_404(request_id)
        asset = Asset.query.get(retrieval_request.asset_id)
        application = StorageApplication.query.get(asset.storage_application_id)
        
        if application.user_id != user.get('id'):
            return jsonify({'error': 'Unauthorized'}), 403
        
        if retrieval_request.status != RetrievalStatus.PREPARING:
            return jsonify({'error': 'Can only cancel requests in preparing status'}), 400
        
        # 상태 업데이트
        retrieval_request.status = RetrievalStatus.CANCELLED
        retrieval_request.cancelled_at = datetime.utcnow()
        asset.status = AssetStatus.STORED
        db.session.commit()
        
        return jsonify({
            'success': True,
            'retrieval_request': retrieval_request.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return handle_error(e, "회수 신청 처리 중 오류가 발생했습니다.")

@retrieval_bp.route('/<int:request_id>', methods=['GET'])
def get_retrieval(request_id):
    """회수 신청 상세 조회"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        retrieval_request = RetrievalRequest.query.get_or_404(request_id)
        asset = Asset.query.get(retrieval_request.asset_id)
        application = StorageApplication.query.get(asset.storage_application_id)
        
        if application.user_id != user.get('id'):
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'success': True,
            'retrieval_request': retrieval_request.to_dict()
        }), 200
        
    except Exception as e:
        return handle_error(e, "회수 신청 처리 중 오류가 발생했습니다.")

