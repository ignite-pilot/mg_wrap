from unittest.mock import patch
from app import db
from app.models import StorageType, ApplicationStatus

class TestSecurity:
    """보안 테스트 (TEST_CHECKLIST 15.1, 15.2)"""
    
    @patch('app.services.member_service.MemberService.verify_token')
    def test_jwt_token_validation(self, mock_verify, client, auth_headers):
        """JWT 토큰 유효성 검증 (15.1) - ig-member API 사용"""
        mock_verify.return_value = {
            'id': 1,
            'email': 'test_unit@example.com',
            'name': 'Test User Unit'
        }
        response = client.post('/api/auth/verify', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_unauthorized_access_prevention(self, client, app):
        """무단 접근 방지 (15.1, 15.2)"""
        # 인증 없이 보호된 엔드포인트 접근 시도
        response = client.get('/api/storage/list')
        assert response.status_code == 401
    
    @patch('app.services.member_service.MemberService.verify_token')
    def test_user_data_isolation(self, mock_verify, client, app, auth_headers):
        """사용자별 데이터 격리 확인 (15.2, 14.2)"""
        # 현재 사용자 모킹 (user_id=1)
        mock_verify.return_value = {
            'id': 1,
            'email': 'test_unit@example.com',
            'name': 'Test User Unit'
        }
        
        with app.app_context():
            # 다른 사용자(user_id=2)의 보관 신청 생성
            from app.models import StorageApplication
            other_app = StorageApplication(
                user_id=2,  # 다른 사용자 ID
                storage_type=StorageType.SPACE,
                space_pyeong=5,
                months=1,
                estimated_price=300000,
                status=ApplicationStatus.APPROVED
            )
            db.session.add(other_app)
            db.session.commit()
            
            # 현재 사용자(user_id=1)로 다른 사용자의 신청 조회 시도
            response = client.get(
                f'/api/storage/{other_app.id}',
                headers=auth_headers
            )
            assert response.status_code == 403  # Forbidden

