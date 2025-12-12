import pytest
import os
from unittest.mock import patch
from app import create_app, db
from app.models import StorageApplication

@pytest.fixture
def app():
    """테스트용 Flask 앱 생성"""
    # 현재 설정된 PostgreSQL 사용 (DB 변경하지 않음)
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['IG_MEMBER_API_URL'] = 'http://localhost:8201/api'
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        # 테스트 전 데이터 정리 (기존 데이터는 유지)
        yield app

@pytest.fixture
def client(app):
    """테스트 클라이언트"""
    return app.test_client()

@pytest.fixture(autouse=True)
def mock_member_service():
    """모든 테스트에서 MemberService 모킹"""
    with patch('app.services.member_service.MemberService.verify_token') as mock_verify:
        # 기본적으로 테스트 사용자 반환
        mock_verify.return_value = {
            'id': 1,
            'email': 'test_unit@example.com',
            'name': 'Test User Unit'
        }
        yield mock_verify

@pytest.fixture
def auth_headers(app):
    """인증된 사용자의 헤더 생성 - ig-member 토큰 사용"""
    # ig-member에서 발급한 테스트 토큰 사용
    test_token = os.getenv('TEST_MEMBER_TOKEN', 'test-token-from-ig-member')
    return {'Authorization': f'Bearer {test_token}'}

@pytest.fixture
def test_user(app):
    """테스트용 사용자 - ig-member 사용자 정보 (딕셔너리)"""
    # ig-member에서 반환하는 사용자 정보 형식
    return {
        'id': 1,
        'email': 'test_unit@example.com',
        'name': 'Test User Unit'
    }

@pytest.fixture
def test_storage_application(app, test_user):
    """테스트용 보관 신청"""
    with app.app_context():
        from app.models import StorageType, ApplicationStatus
        # 기존 신청 확인 또는 생성
        # PostgreSQL ENUM은 소문자이므로, filter_by 대신 filter를 사용
        user_id = test_user.get('id') if isinstance(test_user, dict) else test_user.id
        application = StorageApplication.query.filter(
            StorageApplication.user_id == user_id,
            StorageApplication.space_pyeong == 10
        ).first()
        
        if not application:
            application = StorageApplication(
                user_id=user_id,
                storage_type=StorageType.SPACE,  # Enum 객체 사용 (SQLAlchemy가 자동 변환)
                space_pyeong=10,
                months=3,
                estimated_price=1600000,
                status=ApplicationStatus.APPROVED
            )
            db.session.add(application)
            db.session.commit()
        return application

