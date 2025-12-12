import time
from datetime import date
from app import db
from app.models import Asset, RetrievalRequest, AssetStatus, RetrievalStatus

class TestRetrievalAPI:
    """회수 현황 API 테스트 (TEST_CHECKLIST 5.1, 5.2, 5.3, 10.1, 10.2, 10.3)"""
    
    def test_request_retrieval_success(self, client, auth_headers, test_storage_application):
        """회수 신청 성공 (5.1, 10.1, 10.3)"""
        # 먼저 자산 생성 (고유한 번호 사용)
        unique_num = int(time.time() * 1000) % 10000 + 1
        with db.session.begin():
            asset = Asset(
                asset_number=f'ASSET-2024-{unique_num:04d}',
                storage_application_id=test_storage_application.id,
                application_date=date(2024, 1, 1),
                asset_category='office_supplies',
                status=AssetStatus.STORED
            )
            db.session.add(asset)
            db.session.flush()
            asset_id = asset.id
        
        response = client.post('/api/retrieval/request',
            json={'asset_id': asset_id},
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'retrieval_request' in data
        assert data['retrieval_request']['status'] == 'preparing'  # 5.2
        
        # 자산 상태 확인
        asset = Asset.query.get(asset_id)
        assert asset.status == AssetStatus.RETRIEVAL_REQUESTED
    
    def test_request_retrieval_missing_asset_id(self, client, auth_headers):
        """자산 ID 누락 테스트 (11.2)"""
        response = client.post('/api/retrieval/request',
            json={},
            headers=auth_headers
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_list_retrievals_success(self, client, auth_headers, test_storage_application):
        """회수 현황 목록 조회 성공 (5.1, 10.2)"""
        # 자산 및 회수 신청 생성 (고유한 번호 사용)
        unique_num = int(time.time() * 1000) % 10000 + 2
        with db.session.begin():
            asset = Asset(
                asset_number=f'ASSET-2024-{unique_num:04d}',
                storage_application_id=test_storage_application.id,
                application_date=date(2024, 1, 1),
                asset_category='office_supplies',
                status=AssetStatus.RETRIEVAL_REQUESTED
            )
            db.session.add(asset)
            db.session.flush()
            
            retrieval = RetrievalRequest(
                asset_id=asset.id,
                status=RetrievalStatus.PREPARING
            )
            db.session.add(retrieval)
        
        response = client.get('/api/retrieval/list', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'retrieval_requests' in data
        assert len(data['retrieval_requests']) >= 1
    
    def test_cancel_retrieval_success(self, client, auth_headers, test_storage_application):
        """회수 취소 성공 (5.3, 10.3)"""
        # 자산 및 회수 신청 생성 (고유한 번호 사용)
        unique_num = int(time.time() * 1000) % 10000 + 3
        with db.session.begin():
            asset = Asset(
                asset_number=f'ASSET-2024-{unique_num:04d}',
                storage_application_id=test_storage_application.id,
                application_date=date(2024, 1, 1),
                asset_category='office_supplies',
                status=AssetStatus.RETRIEVAL_REQUESTED
            )
            db.session.add(asset)
            db.session.flush()
            
            retrieval = RetrievalRequest(
                asset_id=asset.id,
                status=RetrievalStatus.PREPARING  # 5.3: 출고 준비중 상태
            )
            db.session.add(retrieval)
            db.session.flush()
            retrieval_id = retrieval.id
        
        response = client.post(
            f'/api/retrieval/{retrieval_id}/cancel',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['retrieval_request']['status'] == 'cancelled'  # 5.2
        
        # 자산 상태 확인
        asset = Asset.query.get(asset.id)
        assert asset.status == AssetStatus.STORED
    
    def test_cancel_retrieval_invalid_status(self, client, auth_headers, test_storage_application):
        """회수 취소 불가 상태 테스트 (5.3) - 출고중"""
        # 자산 및 회수 신청 생성 (출고중 상태, 고유한 번호 사용)
        unique_num = int(time.time() * 1000) % 10000 + 4
        with db.session.begin():
            asset = Asset(
                asset_number=f'ASSET-2024-{unique_num:04d}',
                storage_application_id=test_storage_application.id,
                application_date=date(2024, 1, 1),
                asset_category='office_supplies',
                status=AssetStatus.RETRIEVAL_REQUESTED
            )
            db.session.add(asset)
            db.session.flush()
            
            retrieval = RetrievalRequest(
                asset_id=asset.id,
                status=RetrievalStatus.IN_TRANSIT  # 출고중
            )
            db.session.add(retrieval)
            db.session.flush()
            retrieval_id = retrieval.id
        
        response = client.post(
            f'/api/retrieval/{retrieval_id}/cancel',
            headers=auth_headers
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

