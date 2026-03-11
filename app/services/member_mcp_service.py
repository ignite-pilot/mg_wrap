"""ig-member MCP 서비스 클라이언트"""
import os
from typing import Optional, Dict, Any

# ig-member MCP 서버 설정
IG_MEMBER_MCP_SERVER_URL = os.getenv('IG_MEMBER_MCP_SERVER_URL', 'http://localhost:8202')
IG_MEMBER_API_URL = os.getenv('IG_MEMBER_API_URL', 'https://ig-member.ig-pilot.com/api')

class MemberMCPService:
    """ig-member MCP 서비스 클라이언트"""
    
    @staticmethod
    def _call_mcp(method: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        MCP 서버에 요청을 보내는 내부 메서드
        MCP 프로토콜에 따라 요청을 구성하고 응답을 처리합니다.
        """
        try:
            import requests
            
            # MCP 요청 형식 (JSON-RPC 2.0 기반)
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params or {}
            }
            
            response = requests.post(
                f"{IG_MEMBER_MCP_SERVER_URL}/mcp",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('error'):
                    # 애플리케이션 컨텍스트가 있을 때만 로깅
                    try:
                        from flask import has_app_context, current_app
                        if has_app_context():
                            current_app.logger.error(f"MCP error: {result.get('error')}")
                        else:
                            print(f"MCP error: {result.get('error')}")
                    except Exception:
                        print(f"MCP error: {result.get('error')}")
                    return None
                return result.get('result')
            
            # MCP 서버가 없거나 응답하지 않는 경우, 직접 API 호출로 폴백
            try:
                from flask import has_app_context, current_app
                if has_app_context():
                    current_app.logger.warning("MCP server not available, falling back to direct API call")
                else:
                    print("MCP server not available, falling back to direct API call")
            except Exception:
                print("MCP server not available, falling back to direct API call")
            return None
            
        except Exception as e:
            # 애플리케이션 컨텍스트가 있을 때만 로깅
            try:
                from flask import has_app_context, current_app
                if has_app_context():
                    current_app.logger.warning(f"MCP call failed: {str(e)}, falling back to direct API")
                else:
                    print(f"MCP call failed: {str(e)}, falling back to direct API")
            except Exception:
                print(f"MCP call failed: {str(e)}, falling back to direct API")
            return None
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        토큰 검증 및 사용자 정보 조회 (MCP 우선, 실패 시 직접 API 호출)
        """
        # MCP를 통한 호출 시도
        mcp_result = MemberMCPService._call_mcp(
            "verify_token",
            {"token": token}
        )
        
        if mcp_result:
            return mcp_result
        
        # MCP 실패 시 직접 API 호출로 폴백
        try:
            import requests
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
                if api_response.get('success') and api_response.get('data'):
                    return api_response.get('data')
            return None
        except Exception as e:
            # 애플리케이션 컨텍스트가 있을 때만 로깅
            try:
                from flask import has_app_context, current_app
                if has_app_context():
                    current_app.logger.error(f"Member service error: {str(e)}")
                else:
                    print(f"Member service error: {str(e)}")
            except Exception:
                print(f"Member service error: {str(e)}")
            return None
    
    @staticmethod
    def oauth2_authorization_url(provider: str, redirect_uri: str) -> Optional[str]:
        """
        OAuth2 인증 URL 생성 (MCP 우선, 실패 시 직접 URL 생성)
        """
        # MCP를 통한 호출 시도
        mcp_result = MemberMCPService._call_mcp(
            "oauth2_authorization_url",
            {
                "provider": provider,
                "redirect_uri": redirect_uri
            }
        )
        
        if mcp_result and mcp_result.get('url'):
            return mcp_result.get('url')
        
        # MCP 실패 시 직접 URL 생성으로 폴백
        return f"{IG_MEMBER_API_URL}/login/oauth2/authorization/{provider}?redirect_uri={redirect_uri}"
    
    @staticmethod
    def exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
        """
        OAuth2 코드를 토큰으로 교환 (MCP 우선, 실패 시 직접 API 호출)
        """
        # MCP를 통한 호출 시도
        mcp_result = MemberMCPService._call_mcp(
            "exchange_code_for_token",
            {"code": code}
        )
        
        if mcp_result:
            return mcp_result
        
        # MCP 실패 시 직접 API 호출로 폴백
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
                if token_data.get('success'):
                    return token_data.get('data', {})
                return token_data
            return None
        except Exception as e:
            # 애플리케이션 컨텍스트가 있을 때만 로깅
            try:
                from flask import has_app_context, current_app
                if has_app_context():
                    current_app.logger.error(f"Token exchange error: {str(e)}")
                else:
                    print(f"Token exchange error: {str(e)}")
            except Exception:
                print(f"Token exchange error: {str(e)}")
            return None
    
    @staticmethod
    def login(email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        이메일/비밀번호 로그인 (MCP 우선, 실패 시 직접 API 호출)
        """
        # MCP를 통한 호출 시도
        mcp_result = MemberMCPService._call_mcp(
            "login",
            {
                "email": email,
                "password": password
            }
        )
        
        if mcp_result:
            return mcp_result
        
        # MCP 실패 시 직접 API 호출로 폴백
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
            # 애플리케이션 컨텍스트가 있을 때만 로깅
            try:
                from flask import has_app_context, current_app
                if has_app_context():
                    current_app.logger.error(f"Login error: {str(e)}")
                else:
                    print(f"Login error: {str(e)}")
            except Exception:
                print(f"Login error: {str(e)}")
            return None

