"""
MySQL 전환 테스트 케이스

이 테스트는 PostgreSQL에서 MySQL로 전환한 후 
모든 기능이 정상적으로 작동하는지 확인합니다.
"""
import unittest
import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import StorageApplication, Asset, RetrievalRequest, DisposalRequest
from app.utils.aws_secrets import get_mysql_info


class TestMySQLMigration(unittest.TestCase):
    """MySQL 전환 테스트"""
    
    @classmethod
    def setUpClass(cls):
        """테스트 클래스 초기화"""
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = cls.app.config['SQLALCHEMY_DATABASE_URI']
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
    
    @classmethod
    def tearDownClass(cls):
        """테스트 클래스 정리"""
        cls.app_context.pop()
    
    def setUp(self):
        """각 테스트 전 실행"""
        # 테스트용 트랜잭션 시작
        db.session.begin()
    
    def tearDown(self):
        """각 테스트 후 실행"""
        # 롤백하여 테스트 데이터 제거
        db.session.rollback()
    
    def test_mysql_connection_info(self):
        """MySQL 연결 정보가 올바르게 가져와지는지 테스트"""
        mysql_info = get_mysql_info()
        self.assertIsNotNone(mysql_info, "MySQL 연결 정보를 가져올 수 있어야 합니다")
        self.assertIn('host', mysql_info or {}, "host 정보가 있어야 합니다")
        self.assertIn('user', mysql_info or {}, "user 정보가 있어야 합니다")
        self.assertIn('password', mysql_info or {}, "password 정보가 있어야 합니다")
    
    def test_database_uri_format(self):
        """데이터베이스 URI가 MySQL 형식인지 테스트"""
        db_uri = self.app.config['SQLALCHEMY_DATABASE_URI']
        self.assertIsNotNone(db_uri, "데이터베이스 URI가 설정되어 있어야 합니다")
        self.assertTrue(
            db_uri.startswith('mysql+pymysql://'),
            f"데이터베이스 URI가 MySQL 형식이어야 합니다. 현재: {db_uri[:20]}..."
        )
    
    def test_database_connection(self):
        """데이터베이스 연결 테스트"""
        try:
            # 간단한 쿼리 실행
            result = db.session.execute(db.text("SELECT 1"))
            self.assertIsNotNone(result, "데이터베이스 연결이 성공해야 합니다")
        except Exception as e:
            self.fail(f"데이터베이스 연결 실패: {e}")
    
    def test_table_creation(self):
        """테이블 생성 테스트 (SQLAlchemy ORM)"""
        try:
            # 테이블이 존재하는지 확인
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = [
                'storage_applications',
                'assets',
                'retrieval_requests',
                'disposal_requests'
            ]
            
            for table in expected_tables:
                self.assertIn(
                    table,
                    tables,
                    f"테이블 '{table}'이 존재해야 합니다"
                )
        except Exception as e:
            self.fail(f"테이블 확인 실패: {e}")
    
    def test_enum_type_compatibility(self):
        """Enum 타입이 MySQL과 호환되는지 테스트"""
        from app.models import StorageType, ApplicationStatus, AssetCategory
        
        # Enum 값들이 문자열로 저장되는지 확인
        self.assertIsInstance(StorageType.SPACE.value, str)
        self.assertIsInstance(ApplicationStatus.PENDING.value, str)
        self.assertIsInstance(AssetCategory.OFFICE_SUPPLIES.value, str)
    
    def test_query_compatibility(self):
        """기본 쿼리가 MySQL과 호환되는지 테스트"""
        try:
            # COUNT 쿼리
            count = StorageApplication.query.count()
            self.assertIsInstance(count, int)
            
            # 필터 쿼리
            apps = StorageApplication.query.filter_by(status='pending').all()
            self.assertIsInstance(apps, list)
            
            # JOIN 쿼리
            assets = Asset.query.join(StorageApplication).all()
            self.assertIsInstance(assets, list)
        except Exception as e:
            self.fail(f"쿼리 실행 실패: {e}")
    
    def test_like_query_compatibility(self):
        """LIKE 쿼리가 MySQL과 호환되는지 테스트"""
        try:
            from app.models import Asset
            from datetime import datetime
            
            year = datetime.now().year
            # LIKE 쿼리 실행 (에러가 발생하지 않으면 성공)
            assets = Asset.query.filter(
                Asset.asset_number.like(f'ASSET-{year}-%')
            ).all()
            self.assertIsInstance(assets, list)
        except Exception as e:
            self.fail(f"LIKE 쿼리 실행 실패: {e}")
    
    def test_datetime_compatibility(self):
        """날짜/시간 처리가 MySQL과 호환되는지 테스트"""
        from datetime import datetime
        from app.models import StorageApplication, StorageType, ApplicationStatus
        
        try:
            # 날짜가 포함된 레코드 생성 테스트 (실제로는 저장하지 않음)
            test_app = StorageApplication(
                user_id=1,
                storage_type=StorageType.SPACE,
                space_pyeong=5,
                months=1,
                estimated_price=300000,
                status=ApplicationStatus.PENDING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # 객체가 올바르게 생성되는지 확인
            self.assertIsNotNone(test_app.created_at)
            self.assertIsNotNone(test_app.updated_at)
            self.assertIsInstance(test_app.created_at, datetime)
        except Exception as e:
            self.fail(f"날짜/시간 처리 실패: {e}")


if __name__ == '__main__':
    unittest.main()
