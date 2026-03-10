"""인증 라우트 - ig-member API 사용"""
from flask import Blueprint, request, jsonify
import os
from app.services.member_service import MemberService
from app.utils import handle_error

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/oauth2/authorization/<provider>', methods=['GET', 'OPTIONS'])
def oauth2_authorization(provider):
    """
    OAuth2 인증 리다이렉트
    provider: google, naver 등
    
    Spring Boot OAuth2의 기본 엔드포인트는 /login/oauth2/authorization/{provider}입니다.
    ig-member의 context-path가 /api이므로 실제 경로는 /api/login/oauth2/authorization/{provider}입니다.
    """
    try:
        from flask import redirect, request, make_response
        
        # OPTIONS 요청 처리 (CORS preflight)
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
        
        # 콜백 URL 설정 (mg_wrap으로 돌아올 URL)
        # request.url_root는 프록시를 통해 요청이 올 때 올바르게 설정되지 않을 수 있으므로
        # Host 헤더를 사용하여 URL 구성
        host = request.headers.get('Host', 'localhost:8400')
        scheme = request.headers.get('X-Forwarded-Proto', 'http')
        if ':' not in host:
            # 포트가 없는 경우 기본 포트 추가
            if scheme == 'https':
                host = f"{host}:443"
            else:
                host = f"{host}:8400"
        
        callback_url = f"{scheme}://{host}/api/auth/oauth2/callback"
        
        # ig-member API를 통한 OAuth2 인증 URL 생성
        IG_MEMBER_API_URL = os.getenv('IG_MEMBER_API_URL', 'http://localhost:8201/api')
        oauth_url = f"{IG_MEMBER_API_URL}/login/oauth2/authorization/{provider}?redirect_uri={callback_url}"
        
        # 디버깅: 리다이렉트 URL 로깅
        from flask import current_app
        current_app.logger.info(f"OAuth2 redirect to: {oauth_url}")
        
        return redirect(oauth_url)
        
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"OAuth2 authorization error: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return handle_error(e, 'OAuth 인증 리다이렉트 중 오류가 발생했습니다.')

@auth_bp.route('/oauth2/callback', methods=['GET'])
def oauth2_callback():
    """
    OAuth2 콜백 처리 (ig-member에서 리다이렉트)
    """
    try:
        from flask import redirect, request
        
        # ig-member에서 전달된 토큰 또는 코드 확인
        code = request.args.get('code')
        token = request.args.get('token')
        error = request.args.get('error')
        
        if error:
            return redirect(f"/login?error={error}")
        
        # 토큰이 직접 전달된 경우
        if token:
            # ig-member API를 통한 토큰 검증
            user = MemberService.verify_token(token)
            if user:
                # 프론트엔드로 리다이렉트 (토큰 포함)
                frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:8400')
                return redirect(f"{frontend_url}/login?token={token}")
            else:
                return redirect("/login?error=invalid_token")
        
        # Authorization code가 전달된 경우 (ig-member의 일회용 코드)
        if code:
            # ig-member API를 통한 코드 교환
            token_data = MemberService.exchange_code_for_token(code)
            
            if token_data:
                # 토큰 추출
                access_token = (
                    token_data.get('token') or 
                    token_data.get('accessToken') or 
                    token_data.get('access_token')
                )
                
                if access_token:
                    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:8400')
                    return redirect(f"{frontend_url}/login?token={access_token}")
        
        return redirect("/login?error=oauth_callback_failed")
        
    except Exception as e:
        from flask import redirect
        return redirect(f"/login?error={str(e)}")

@auth_bp.route('/google', methods=['POST'])
def google_auth():
    """
    구글 OAuth 인증 - ig-member OAuth2 플로우 사용
    프론트엔드에서 ig-member의 OAuth2 플로우를 따르도록 변경됨
    이 엔드포인트는 호환성을 위해 유지하되, ig-member로 리다이렉트하도록 안내
    """
    return jsonify({
        'error': 'Deprecated',
        'message': 'Google 로그인은 ig-member 서비스를 통해 처리됩니다. 프론트엔드에서 ig-member OAuth2 플로우를 사용해주세요.',
        'redirect_url': os.getenv('IG_MEMBER_FRONTEND_URL', 'http://localhost:8200')
    }), 301

@auth_bp.route('/login', methods=['POST'])
def login():
    """자체 로그인 (ig-member API 프록시)"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # ig-member API를 통한 로그인
        login_result = MemberService.login(email, password)
        
        # 디버깅: login_result 구조 확인
        from flask import current_app
        current_app.logger.info(f"Login result type: {type(login_result)}, value: {login_result}")
        
        if login_result:
            # login_result는 ig-member API의 data 부분
            # data 안에 token이 있을 수도 있고, 전체가 token일 수도 있음
            token = (
                login_result.get('token') if isinstance(login_result, dict) else None or 
                login_result.get('accessToken') if isinstance(login_result, dict) else None or
                login_result.get('access_token') if isinstance(login_result, dict) else None or
                (login_result if isinstance(login_result, str) else None)
            )
            user = login_result.get('user') if isinstance(login_result, dict) else login_result
            
            current_app.logger.info(f"Extracted token: {token is not None}, user: {user is not None}")
            
            # token이 문자열이거나 딕셔너리에 token이 있는 경우
            if token:
                return jsonify({
                    'success': True,
                    'token': token if isinstance(token, str) else str(token),
                    'user': user
                }), 200
        
        current_app.logger.warning(f"Login failed for email: {email}")
        return jsonify({
            'success': False,
            'error': '로그인 실패'
        }), 401
        
    except Exception as e:
        return handle_error(e, '로그인 중 오류가 발생했습니다.')

@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """토큰 검증 (ig-member API 사용)"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 401
        
        # ig-member API를 통한 토큰 검증
        user = MemberService.verify_token(token)
        
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        
        return jsonify({
            'success': True,
            'user': user
        }), 200
        
    except Exception as e:
        return handle_error(e, '토큰 검증 중 오류가 발생했습니다.')

def get_current_user():
    """현재 사용자 가져오기 (ig-member API 사용)"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    
    try:
        # ig-member API를 통한 토큰 검증
        user = MemberService.verify_token(token)
        return user
    except Exception:
        return None
