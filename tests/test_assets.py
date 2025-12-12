from datetime import date
from app import db
from app.models import Asset, AssetCategory, AssetStatus
from app.routes.assets import generate_asset_number

class TestAssetNumberGeneration:
    """자산번호 생성 테스트 (TEST_CHECKLIST 4.5)"""
    
    def test_generate_asset_number(self, app):
        """자산번호 생성 테스트 - ASSET-YYYY-XXX 형식"""
        with app.app_context():
            asset_number = generate_asset_number()
            assert asset_number.startswith('ASSET-')
            assert len(asset_number.split('-')) == 3
            year = str(date.today().year)
            assert year in asset_number

class TestAssetsAPI:
    """자산 관리 API 테스트 (TEST_CHECKLIST 4.2, 4.5, 10.1, 10.4)"""
    
    def test_create_asset_success(self, client, auth_headers, test_storage_application):
        """자산 등록 성공 (4.2, 10.1, 10.4)"""
        response = client.post('/api/assets/create',
            json={
                'storage_application_id': test_storage_application.id,
                'application_date': '2024-01-01',
                'asset_category': 'office_supplies',
                'special_notes': '테스트 자산'
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'asset' in data
        assert data['asset']['asset_category'] == 'office_supplies'
        assert data['asset']['storage_start_date'] is None  # NULL 허용 (10.4)
    
    def test_create_asset_with_storage_start_date(self, client, auth_headers, test_storage_application):
        """보관 시작일 포함 자산 등록 (4.2)"""
        response = client.post('/api/assets/create',
            json={
                'storage_application_id': test_storage_application.id,
                'application_date': '2024-01-01',
                'storage_start_date': '2024-01-15',
                'asset_category': 'documents',
                'special_notes': '문서 보관'
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['asset']['storage_start_date'] == '2024-01-15'
    
    def test_create_asset_missing_fields(self, client, auth_headers):
        """필수 필드 누락 테스트 (11.2)"""
        response = client.post('/api/assets/create',
            json={
                'asset_category': 'office_supplies'
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_asset_invalid_category(self, client, auth_headers, test_storage_application):
        """잘못된 자산 분류 테스트 (4.4, 11.2)"""
        response = client.post('/api/assets/create',
            json={
                'storage_application_id': test_storage_application.id,
                'application_date': '2024-01-01',
                'asset_category': 'invalid_category',
                'special_notes': '테스트'
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_list_assets_success(self, client, auth_headers, test_storage_application):
        """자산 목록 조회 성공 (4.5, 10.2)"""
        # 먼저 자산 생성 (고유한 번호 사용)
        import time
        unique_num = int(time.time() * 1000) % 10000
        with db.session.begin():
            asset = Asset(
                asset_number=f'ASSET-2024-{unique_num:04d}',
                storage_application_id=test_storage_application.id,
                application_date=date(2024, 1, 1),
                asset_category=AssetCategory.OFFICE_SUPPLIES,
                status=AssetStatus.STORED
            )
            db.session.add(asset)
        
        response = client.get('/api/assets/list', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'assets' in data
        assert len(data['assets']) >= 1
    
    def test_list_assets_filter_by_application(self, client, auth_headers, test_storage_application):
        """보관 신청별 자산 필터링 (4.1)"""
        # 자산 생성 (고유한 번호 사용)
        import time
        unique_num = int(time.time() * 1000) % 10000 + 1
        with db.session.begin():
            asset = Asset(
                asset_number=f'ASSET-2024-{unique_num:04d}',
                storage_application_id=test_storage_application.id,
                application_date=date(2024, 1, 1),
                asset_category=AssetCategory.DOCUMENTS,
                status=AssetStatus.STORED
            )
            db.session.add(asset)
        
        response = client.get(
            f'/api/assets/list?storage_application_id={test_storage_application.id}',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert all(a['storage_application_id'] == test_storage_application.id 
                  for a in data['assets'])

