from unittest.mock import patch

class TestAuth:
    """인증 관련 테스트 - ig-member API 사용"""
    
    @patch('app.services.member_service.MemberService.verify_token')
    def test_verify_token_success(self, mock_verify, client):
        """토큰 검증 성공 테스트 - ig-member API 사용"""
        # ig-member에서 반환하는 사용자 정보 모킹
        mock_verify.return_value = {
            'id': 1,
            'email': 'test_unit@example.com',
            'name': 'Test User Unit'
        }
        
        headers = {'Authorization': 'Bearer test-token'}
        response = client.post('/api/auth/verify', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'user' in data
        assert data['user']['email'] == 'test_unit@example.com'
    
    def test_verify_token_missing(self, client):
        """토큰 없이 검증 시도 테스트"""
        response = client.post('/api/auth/verify')
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    @patch('app.services.member_service.MemberService.verify_token')
    def test_verify_token_invalid(self, mock_verify, client):
        """잘못된 토큰 검증 테스트"""
        mock_verify.return_value = None  # 토큰 검증 실패
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.post('/api/auth/verify', headers=headers)
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_google_auth_deprecated(self, client):
        """Google 인증 엔드포인트가 deprecated되었는지 테스트"""
        response = client.post('/api/auth/google', json={'token': 'test'})
        assert response.status_code == 301
        data = response.get_json()
        assert 'Deprecated' in data.get('error', '')
    
    @patch('app.services.member_service.MemberService.verify_token')
    def test_get_current_user_success(self, mock_verify, app):
        """현재 사용자 가져오기 성공 테스트"""
        from app.routes.auth import get_current_user
        
        mock_verify.return_value = {
            'id': 1,
            'email': 'test_unit@example.com',
            'name': 'Test User Unit'
        }
        
        headers = {'Authorization': 'Bearer test-token'}
        with app.test_request_context(headers=headers):
            user = get_current_user()
            assert user is not None
            assert user.get('email') == 'test_unit@example.com'
    
    def test_get_current_user_no_token(self, app):
        """토큰 없이 현재 사용자 가져오기 테스트"""
        from app.routes.auth import get_current_user
        
        with app.test_request_context():
            user = get_current_user()
            assert user is None

