from flask import Blueprint, request, jsonify
import requests
import os

board_bp = Blueprint('board', __name__)

# ig-board API 기본 URL
IG_BOARD_API_URL = os.getenv('IG_BOARD_API_URL', 'http://localhost:8301')

# 문의하기 게시판 ID (환경 변수로 설정 가능)
INQUIRY_BOARD_ID = int(os.getenv('INQUIRY_BOARD_ID', '2'))

# ig-board SECRET_KEY (토큰 생성용, 환경 변수로 설정)
IG_BOARD_SECRET_KEY = os.getenv('IG_BOARD_SECRET_KEY')
IG_BOARD_ALGORITHM = os.getenv('IG_BOARD_ALGORITHM', 'HS256')

if not IG_BOARD_SECRET_KEY:
    import warnings
    warnings.warn(
        "IG_BOARD_SECRET_KEY is not set. Board integration may not work properly. "
        "Set it in .env file for production use."
    )

def get_ig_board_token(mg_wrap_user):
    """mg_wrap 사용자 정보를 사용하여 ig-board 토큰 생성"""
    try:
        from datetime import datetime, timedelta, timezone
        import jwt
        
        # mg_wrap_user는 딕셔너리 (ig-member에서 반환)
        user_email = mg_wrap_user.get('email') if isinstance(mg_wrap_user, dict) else mg_wrap_user.email
        
        # ig-board에 사용자 등록/조회
        # 먼저 ig-board에서 사용자를 찾거나 생성
        ig_board_user_url = f"{IG_BOARD_API_URL}/api/admin/users/by-email"
        user_response = requests.get(
            ig_board_user_url,
            params={'email': user_email},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        user_id = None
        user_role = 'user'
        
        if user_response.status_code == 200:
            # 사용자가 이미 존재함
            user_data = user_response.json()
            user_id = user_data.get('id')
            user_role = user_data.get('role', 'user')
        else:
            # 사용자가 없으면 생성 시도 (실패할 수 있음)
            # 실제로는 ig-board API를 통해 사용자를 생성해야 함
            pass
        
        # 토큰 생성 (ig-board의 create_access_token과 동일한 방식)
        if user_id and IG_BOARD_SECRET_KEY:
            from datetime import timedelta
            expire = datetime.now(timezone.utc) + timedelta(days=7)
            payload = {
                "sub": user_email,
                "user_id": user_id,
                "role": user_role,
                "exp": expire
            }
            token = jwt.encode(payload, IG_BOARD_SECRET_KEY, algorithm=IG_BOARD_ALGORITHM)
            return token
        
        return None
    except Exception as e:
        print(f"Error getting ig-board token: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_ig_board_headers():
    """ig-board API 호출을 위한 헤더 생성"""
    from app.routes.auth import get_current_user
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    # mg_wrap 사용자 정보 가져오기
    try:
        mg_wrap_user = get_current_user()
        if mg_wrap_user:
            # ig-board 토큰 생성 시도
            ig_board_token = get_ig_board_token(mg_wrap_user)
            if ig_board_token:
                headers['Authorization'] = f'Bearer {ig_board_token}'
            else:
                # 토큰을 얻을 수 없는 경우, 원래 헤더 전달 시도
                # (같은 Google OAuth를 사용한다면 작동할 수 있음)
                auth_header = request.headers.get('Authorization')
                if auth_header:
                    headers['Authorization'] = auth_header
    except Exception as e:
        # 인증 실패 시 원래 헤더 전달 시도
        print(f"Warning: Could not get user for ig-board auth: {e}")
        auth_header = request.headers.get('Authorization')
        if auth_header:
            headers['Authorization'] = auth_header
    
    return headers

@board_bp.route('/posts', methods=['GET'])
def get_posts():
    """게시글 목록 조회"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        url = f"{IG_BOARD_API_URL}/api/posts"
        params = {
            'board_id': INQUIRY_BOARD_ID,
            'page': page,
            'per_page': per_page
        }
        
        # 헤더 생성 시 예외가 발생할 수 있으므로 안전하게 처리
        try:
            headers = get_ig_board_headers()
        except Exception as e:
            from flask import current_app
            current_app.logger.warning(f"Failed to get board headers: {str(e)}")
            headers = {'Content-Type': 'application/json'}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout', 'detail': '게시판 서버 응답이 없습니다.'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Connection error', 'detail': '게시판 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.'}), 503
    except requests.exceptions.RequestException as e:
        from app.utils import handle_error
        return handle_error(e, "게시판 요청 처리 중 오류가 발생했습니다.")
    except Exception as e:
        from app.utils import handle_error
        return handle_error(e, "게시글 목록 조회 중 오류가 발생했습니다.")

@board_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """게시글 상세 조회"""
    try:
        url = f"{IG_BOARD_API_URL}/api/posts/{post_id}"
        
        response = requests.get(url, headers=get_ig_board_headers())
        response.raise_for_status()
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        from app.utils import handle_error
        return handle_error(e, "게시판 요청 처리 중 오류가 발생했습니다.")

@board_bp.route('/posts', methods=['POST'])
def create_post():
    """게시글 작성"""
    try:
        data = request.get_json()
        data['board_id'] = INQUIRY_BOARD_ID
        
        url = f"{IG_BOARD_API_URL}/api/posts"
        headers = get_ig_board_headers()
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        # 응답이 성공적이지 않으면 에러 처리
        if response.status_code >= 400:
            try:
                error_detail = response.json()
                error_message = error_detail.get('detail', error_detail.get('error', 'Unknown error'))
                # 로그에만 상세 정보 기록
                from flask import current_app
                current_app.logger.warning(f"Board API error: {error_message}")
                return jsonify({
                    'error': 'Failed to create post',
                    'message': '게시글 작성에 실패했습니다. 다시 시도해주세요.'
                }), response.status_code
            except Exception:
                from flask import current_app
                current_app.logger.warning(f"Board API error: {response.status_code}")
                return jsonify({
                    'error': 'Failed to create post',
                    'message': '게시글 작성에 실패했습니다. 다시 시도해주세요.'
                }), response.status_code
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout', 'detail': '게시판 서버 응답이 없습니다.'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Connection error', 'detail': '게시판 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.'}), 503
    except requests.exceptions.RequestException as e:
        from flask import current_app
        current_app.logger.error(f"Board API request failed: {str(e)}")
        return jsonify({
            'error': 'Request failed',
            'message': '게시판 서버와 통신 중 오류가 발생했습니다.'
        }), 500
    except Exception as e:
        import traceback
        from flask import current_app
        error_trace = traceback.format_exc()
        current_app.logger.error(f"Board API internal error: {str(e)}")
        current_app.logger.error(f"Traceback: {error_trace}")
        return jsonify({
            'error': 'Internal error',
            'message': '게시글 작성 중 오류가 발생했습니다.'
        }), 500

@board_bp.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """게시글 수정"""
    try:
        data = request.get_json()
        
        url = f"{IG_BOARD_API_URL}/api/posts/{post_id}"
        
        response = requests.put(url, json=data, headers=get_ig_board_headers())
        response.raise_for_status()
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        from app.utils import handle_error
        return handle_error(e, "게시판 요청 처리 중 오류가 발생했습니다.")

@board_bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """게시글 삭제"""
    try:
        url = f"{IG_BOARD_API_URL}/api/posts/{post_id}"
        
        response = requests.delete(url, headers=get_ig_board_headers())
        response.raise_for_status()
        
        return '', response.status_code
    except requests.exceptions.RequestException as e:
        from app.utils import handle_error
        return handle_error(e, "게시판 요청 처리 중 오류가 발생했습니다.")

@board_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """댓글 목록 조회"""
    try:
        url = f"{IG_BOARD_API_URL}/api/comments"
        params = {'post_id': post_id}
        
        response = requests.get(url, params=params, headers=get_ig_board_headers())
        response.raise_for_status()
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        from app.utils import handle_error
        return handle_error(e, "게시판 요청 처리 중 오류가 발생했습니다.")

@board_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    """댓글 작성"""
    try:
        data = request.get_json()
        data['post_id'] = post_id
        
        url = f"{IG_BOARD_API_URL}/api/comments"
        
        response = requests.post(url, json=data, headers=get_ig_board_headers())
        response.raise_for_status()
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        from app.utils import handle_error
        return handle_error(e, "게시판 요청 처리 중 오류가 발생했습니다.")

@board_bp.route('/board', methods=['GET'])
def get_board_info():
    """게시판 정보 조회"""
    try:
        url = f"{IG_BOARD_API_URL}/api/boards/{INQUIRY_BOARD_ID}"
        
        # 헤더 생성 시 예외가 발생할 수 있으므로 안전하게 처리
        try:
            headers = get_ig_board_headers()
        except Exception as e:
            from flask import current_app
            current_app.logger.warning(f"Failed to get board headers: {str(e)}")
            headers = {'Content-Type': 'application/json'}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout', 'detail': '게시판 서버 응답이 없습니다.'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Connection error', 'detail': '게시판 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.'}), 503
    except requests.exceptions.RequestException as e:
        from app.utils import handle_error
        return handle_error(e, "게시판 요청 처리 중 오류가 발생했습니다.")
    except Exception as e:
        from app.utils import handle_error
        return handle_error(e, "게시판 정보 조회 중 오류가 발생했습니다.")

