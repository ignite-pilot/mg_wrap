import time
from datetime import date
from app import db
from app.models import Asset, DisposalRequest, AssetStatus, DisposalStatus

class TestDisposalAPI:
    """폐기 현황 API 테스트 (TEST_CHECKLIST 6.1, 6.2, 6.3, 10.1, 10.2, 10.3)"""
    
    def test_request_disposal_success(self, client, auth_headers, test_storage_application):
        """폐기 신청 성공 (6.1, 10.1, 10.3)"""
        # 먼저 자산 생성 (고유한 번호 사용)
        unique_num = int(time.time() * 1000) % 10000 + 5
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
        
        response = client.post('/api/disposal/request',
            json={'asset_id': asset_id},
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'disposal_request' in data
        assert data['disposal_request']['status'] == 'preparing'  # 6.2
        
        # 자산 상태 확인
        asset = Asset.query.get(asset_id)
        assert asset.status == AssetStatus.DISPOSAL_REQUESTED
    
    def test_request_disposal_missing_asset_id(self, client, auth_headers):
        """자산 ID 누락 테스트 (11.2)"""
        response = client.post('/api/disposal/request',
            json={},
            headers=auth_headers
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_list_disposals_success(self, client, auth_headers, test_storage_application):
        """폐기 현황 목록 조회 성공 (6.1, 10.2)"""
        # 자산 및 폐기 신청 생성 (고유한 번호 사용)
        unique_num = int(time.time() * 1000) % 10000 + 6
        with db.session.begin():
            asset = Asset(
                asset_number=f'ASSET-2024-{unique_num:04d}',
                storage_application_id=test_storage_application.id,
                application_date=date(2024, 1, 1),
                asset_category='office_supplies',
                status=AssetStatus.DISPOSAL_REQUESTED
            )
            db.session.add(asset)
            db.session.flush()
            
            disposal = DisposalRequest(
                asset_id=asset.id,
                status=DisposalStatus.PREPARING
            )
            db.session.add(disposal)
        
        response = client.get('/api/disposal/list', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'disposal_requests' in data
        assert len(data['disposal_requests']) >= 1
    
    def test_cancel_disposal_success(self, client, auth_headers, test_storage_application):
        """폐기 취소 성공 (6.3, 10.3)"""
        # 자산 및 폐기 신청 생성 (고유한 번호 사용)
        unique_num = int(time.time() * 1000) % 10000 + 7
        with db.session.begin():
            asset = Asset(
                asset_number=f'ASSET-2024-{unique_num:04d}',
                storage_application_id=test_storage_application.id,
                application_date=date(2024, 1, 1),
                asset_category='office_supplies',
                status=AssetStatus.DISPOSAL_REQUESTED
            )
            db.session.add(asset)
            db.session.flush()
            
            disposal = DisposalRequest(
                asset_id=asset.id,
                status=DisposalStatus.PREPARING  # 6.3: 폐기 준비중 상태
            )
            db.session.add(disposal)
            db.session.flush()
            disposal_id = disposal.id
        
        response = client.post(
            f'/api/disposal/{disposal_id}/cancel',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['disposal_request']['status'] == 'cancelled'  # 6.2
        
        # 자산 상태 확인
        asset = Asset.query.get(asset.id)
        assert asset.status == AssetStatus.STORED
    
    def test_cancel_disposal_invalid_status(self, client, auth_headers, test_storage_application):
        """폐기 취소 불가 상태 테스트 (6.3) - 폐기 완료"""
        # 자산 및 폐기 신청 생성 (폐기 완료 상태, 고유한 번호 사용)
        unique_num = int(time.time() * 1000) % 10000 + 8
        with db.session.begin():
            asset = Asset(
                asset_number=f'ASSET-2024-{unique_num:04d}',
                storage_application_id=test_storage_application.id,
                application_date=date(2024, 1, 1),
                asset_category='office_supplies',
                status=AssetStatus.DISPOSED
            )
            db.session.add(asset)
            db.session.flush()
            
            disposal = DisposalRequest(
                asset_id=asset.id,
                status=DisposalStatus.COMPLETED  # 폐기 완료
            )
            db.session.add(disposal)
            db.session.flush()
            disposal_id = disposal.id
        
        response = client.post(
            f'/api/disposal/{disposal_id}/cancel',
            headers=auth_headers
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

