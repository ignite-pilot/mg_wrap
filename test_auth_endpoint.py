#!/usr/bin/env python3
"""Google OAuth 엔드포인트 테스트"""
import requests
import json

# 테스트용 더미 토큰 (실제로는 Google에서 받은 토큰이 필요)
test_data = {
    'token': 'test_token_12345'
}

try:
    print("Google OAuth 엔드포인트 테스트 중...")
    print("URL: http://localhost:5000/api/auth/google")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    response = requests.post(
        'http://localhost:5000/api/auth/google',
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
except requests.exceptions.ConnectionError:
    print("❌ 백엔드 서버가 실행 중이지 않습니다.")
    print("   먼저 'python3 run.py'로 서버를 시작해주세요.")
except Exception as e:
    print(f"❌ 오류 발생: {e}")

