"""ig-member 서비스 클라이언트"""
import requests
import os
from typing import Optional, Dict, Any
from flask import current_app

# ig-member API 기본 URL
IG_MEMBER_API_URL = os.getenv('IG_MEMBER_API_URL', 'http://localhost:8201/api')

class MemberService:
    """ig-member API 클라이언트"""
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """토큰 검증 및 사용자 정보 조회"""
        try:
            response = requests.get(
                f"{IG_MEMBER_API_URL}/users/me",
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                api_response = response.json()
                # ig-member는 ApiResponse 형식으로 반환
                if api_response.get('success') and api_response.get('data'):
                    return api_response.get('data')
            return None
        except Exception as e:
            current_app.logger.error(f"Member service error: {str(e)}")
            return None
    
    @staticmethod
    def get_user_by_token(token: str) -> Optional[Dict[str, Any]]:
        """토큰으로 사용자 정보 조회"""
        return MemberService.verify_token(token)
    
    @staticmethod
    def google_auth(google_token: str) -> Optional[Dict[str, Any]]:
        """
        Google OAuth 인증 - Google 토큰을 검증하고 ig-member에 사용자 생성/조회
        ig-member는 OAuth2 리디렉션 방식을 사용하므로, 여기서는 Google 토큰을 검증만 하고
        실제 사용자 관리는 ig-member의 OAuth2 플로우를 따르도록 프론트엔드에서 처리
        """
        try:
            # Google 토큰 검증
            from google.oauth2 import id_token
            from google.auth.transport import requests as google_requests
            
            GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
            if not GOOGLE_CLIENT_ID:
                current_app.logger.error("GOOGLE_CLIENT_ID not configured")
                return None
            
            # Google 토큰 검증
            try:
                idinfo = id_token.verify_oauth2_token(
                    google_token, google_requests.Request(), GOOGLE_CLIENT_ID
                )
                
                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    return None
                
                email = idinfo['email']
                name = idinfo.get('name', email.split('@')[0])
                
            except Exception as e:
                current_app.logger.error(f"Google token verification failed: {str(e)}")
                return None
            
            # ig-member는 OAuth2 리디렉션 방식을 사용하므로,
            # 여기서는 Google 토큰 검증만 하고, 실제 사용자 관리는
            # 프론트엔드에서 ig-member의 OAuth2 플로우를 따르도록 함
            # 또는 ig-member API를 직접 호출하여 사용자 정보 조회
            # 
            # 임시로 검증된 사용자 정보만 반환
            # 실제 구현에서는 ig-member의 OAuth2 콜백을 통해 처리해야 함
            return {
                'email': email,
                'name': name,
                'verified': True
            }
            
        except Exception as e:
            current_app.logger.error(f"Google auth error: {str(e)}")
            return None
    
    @staticmethod
    def oauth2_authorization_url(provider: str, redirect_uri: str) -> str:
        """
        OAuth2 인증 URL 생성
        provider: google, naver 등
        redirect_uri: 콜백 URL
        """
        return f"{IG_MEMBER_API_URL}/login/oauth2/authorization/{provider}?redirect_uri={redirect_uri}"
    
    @staticmethod
    def exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
        """
        OAuth2 코드를 토큰으로 교환
        """
        try:
            import requests
            response = requests.post(
                f"{IG_MEMBER_API_URL}/auth/oauth2/token",
                json={'code': code},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                # ig-member의 ApiResponse 형식 확인
                if token_data.get('success'):
                    return token_data.get('data', {})
                # 직접 토큰이 있는 경우
                return token_data
            return None
        except Exception as e:
            current_app.logger.error(f"Token exchange error: {str(e)}")
            return None
    
    @staticmethod
    def login(email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        이메일/비밀번호 로그인
        """
        try:
            import requests
            response = requests.post(
                f"{IG_MEMBER_API_URL}/auth/login",
                json={'email': email, 'password': password},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                api_response = response.json()
                if api_response.get('success'):
                    return api_response.get('data', {})
            return None
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            return None

