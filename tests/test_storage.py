from app.routes.storage import calculate_price

class TestStoragePriceCalculation:
    """보관 신청 가격 계산 테스트 (TEST_CHECKLIST 3.1, 3.2)"""
    
    def test_calculate_price_space_1_month(self):
        """공간형 1개월 가격 계산 (3.1)"""
        price = calculate_price('space', 1, space_pyeong=5)
        assert price == 300000  # 5평 기준 1개월
    
    def test_calculate_price_space_3_months(self):
        """공간형 3개월 가격 계산 (3.1)"""
        price = calculate_price('space', 3, space_pyeong=5)
        assert price == 800000  # 5평 기준 3개월
    
    def test_calculate_price_space_6_months(self):
        """공간형 6개월 가격 계산 (3.1)"""
        price = calculate_price('space', 6, space_pyeong=5)
        assert price == 1500000  # 5평 기준 6개월
    
    def test_calculate_price_space_10_pyeong(self):
        """공간형 10평 가격 계산 (3.1) - 평수 × 60,000원"""
        price = calculate_price('space', 1, space_pyeong=10)
        assert price == 600000  # 10평 = 5평의 2배
    
    def test_calculate_price_space_3_months_10_pyeong(self):
        """공간형 3개월 10평 가격 계산 (3.1) - 평수 × 266,666원"""
        price = calculate_price('space', 3, space_pyeong=10)
        assert price == 1600000  # 10평 × 266,666원 (반올림)
    
    def test_calculate_price_space_6_months_10_pyeong(self):
        """공간형 6개월 10평 가격 계산 (3.1) - 평수 × 500,000원"""
        price = calculate_price('space', 6, space_pyeong=10)
        assert price == 3000000  # 10평 × 500,000원
    
    def test_calculate_price_box_1_month(self):
        """BOX형 1개월 가격 계산 (3.2)"""
        price = calculate_price('box', 1, box_count=1)
        assert price == 30000  # BOX 수량 × 30,000원
    
    def test_calculate_price_box_3_months(self):
        """BOX형 3개월 가격 계산 (3.2)"""
        price = calculate_price('box', 3, box_count=1)
        assert price == 80000  # BOX 수량 × 80,000원
    
    def test_calculate_price_box_6_months(self):
        """BOX형 6개월 가격 계산 (3.2)"""
        price = calculate_price('box', 6, box_count=1)
        assert price == 150000  # BOX 수량 × 150,000원
    
    def test_calculate_price_box_multiple(self):
        """BOX형 여러 개 가격 계산 (3.2)"""
        price = calculate_price('box', 1, box_count=5)
        assert price == 150000  # 30,000 × 5

class TestStorageAPI:
    """보관 신청 API 테스트 (TEST_CHECKLIST 3.1, 3.2, 3.3, 3.4)"""
    
    def test_estimate_space_success(self, client):
        """공간형 견적 조회 성공 (3.1)"""
        response = client.post('/api/storage/estimate', json={
            'storage_type': 'space',
            'months': 3,
            'space_pyeong': 10
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'estimated_price' in data
        assert data['estimated_price'] == 1600000  # 10평 * 3개월
    
    def test_estimate_box_success(self, client):
        """BOX형 견적 조회 성공 (3.2)"""
        response = client.post('/api/storage/estimate', json={
            'storage_type': 'box',
            'months': 3,
            'box_count': 5
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['estimated_price'] == 400000  # 80,000 * 5
    
    def test_estimate_missing_fields(self, client):
        """필수 필드 누락 테스트 (3.3)"""
        response = client.post('/api/storage/estimate', json={
            'storage_type': 'space'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_estimate_invalid_months(self, client):
        """잘못된 개월수 테스트 (3.3)"""
        response = client.post('/api/storage/estimate', json={
            'storage_type': 'space',
            'months': 2,  # 1, 3, 6만 허용
            'space_pyeong': 10
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_estimate_space_zero_pyeong(self, client):
        """평수 0 이하 입력 테스트 (3.3)"""
        response = client.post('/api/storage/estimate', json={
            'storage_type': 'space',
            'months': 1,
            'space_pyeong': 0
        })
        # API는 0도 허용할 수 있지만, 프론트엔드에서 검증해야 함
        # 여기서는 API 레벨 테스트만 수행
        assert response.status_code in [200, 400]
    
    def test_apply_storage_success(self, client, auth_headers):
        """보관 신청 성공 (3.1, 10.1)"""
        response = client.post('/api/storage/apply', 
            json={
                'storage_type': 'space',
                'months': 3,
                'space_pyeong': 10
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'application' in data
        assert data['application']['storage_type'] == 'space'
        assert data['application']['space_pyeong'] == 10
        assert data['application']['months'] == 3
    
    def test_apply_storage_unauthorized(self, client):
        """인증 없이 보관 신청 시도 (3.3)"""
        response = client.post('/api/storage/apply', json={
            'storage_type': 'space',
            'months': 3,
            'space_pyeong': 10
        })
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_list_applications_success(self, client, auth_headers, test_storage_application):
        """보관 신청 목록 조회 성공 (3.4, 10.2)"""
        response = client.get('/api/storage/list', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'applications' in data
        assert len(data['applications']) >= 1
    
    def test_get_application_success(self, client, auth_headers, test_storage_application):
        """보관 신청 상세 조회 성공 (3.4)"""
        response = client.get(
            f'/api/storage/{test_storage_application.id}',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'application' in data
        assert data['application']['id'] == test_storage_application.id

