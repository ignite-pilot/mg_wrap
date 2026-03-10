from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from app.utils.aws_secrets import get_mysql_info

load_dotenv()

db = SQLAlchemy()

def create_app():
    # Set static folder to frontend/dist for production
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'dist')

    if os.path.exists(static_folder):
        # static_url_path를 빈 문자열로 설정하여 기본 static 라우트 비활성화
        # SPA 라우팅을 위해 직접 처리
        app = Flask(__name__, static_folder=None, static_url_path=None)
    else:
        app = Flask(__name__)

    # Configuration
    # 테스트 프로젝트용 하드코딩된 SECRET_KEY
    app.config['SECRET_KEY'] = 'test-secret-key-for-development-only-do-not-use-in-production'
    
    # MySQL 연결 설정 (AWS Secrets Manager에서 가져오기)
    mysql_info = get_mysql_info()
    if not mysql_info:
        raise ValueError(
            "Failed to retrieve MySQL connection info from AWS Secrets Manager. "
            "Please check 'prod/ignite-pilot/mysql-realpilot' secret."
        )
    
    # Secrets Manager에서 가져온 정보 사용
    db_user = mysql_info.get('user') or mysql_info.get('username') or mysql_info.get('DB_USER')
    db_password = mysql_info.get('password') or mysql_info.get('DB_PASSWORD')
    db_host = mysql_info.get('host') or mysql_info.get('hostname') or mysql_info.get('DB_HOST')
    db_port = mysql_info.get('port') or mysql_info.get('DB_PORT', '3306')
    # db_name은 ig-board로 고정
    db_name = 'ig-board'
    
    # 필수 값 검증
    if not all([db_user, db_password, db_host]):
        raise ValueError(
            "Missing required database connection info from AWS Secrets Manager. "
            "Required fields: user/username, password, host/hostname"
        )
    
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # CORS 설정 - 단일 서비스이므로 같은 origin에서 실행
    # ig-member 서비스와의 통신을 위해 필요한 경우에만 CORS 설정
    cors_origins = os.getenv('CORS_ORIGINS', '').split(',')
    cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]
    
    # ig-member 프론트엔드도 허용 (OAuth 콜백을 위해)
    ig_member_frontend = os.getenv('IG_MEMBER_FRONTEND_URL', 'http://localhost:8200')
    if ig_member_frontend not in cors_origins:
        cors_origins.append(ig_member_frontend)
    
    # CORS가 필요한 경우에만 설정 (단일 서비스에서는 대부분 불필요)
    if cors_origins:
        CORS(app, resources={r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type", "Authorization"]
        }})
    
    # Database 초기화
    db.init_app(app)

    # Blueprint 등록
    from app.routes.auth import auth_bp
    from app.routes.storage import storage_bp
    from app.routes.assets import assets_bp
    from app.routes.retrieval import retrieval_bp
    from app.routes.disposal import disposal_bp
    from app.routes.board import board_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(storage_bp, url_prefix='/api/storage')
    app.register_blueprint(assets_bp, url_prefix='/api/assets')
    app.register_blueprint(retrieval_bp, url_prefix='/api/retrieval')
    app.register_blueprint(disposal_bp, url_prefix='/api/disposal')
    app.register_blueprint(board_bp, url_prefix='/api/board')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy'}), 200

    # 정적 파일 폴더 경로 저장 (static_folder는 None으로 설정했으므로 별도로 관리)
    static_folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'dist')
    
    # Serve React App (SPA fallback)
    # 단일 서비스: Flask가 frontend와 backend를 모두 서빙
    # 이 라우트는 마지막에 등록되어야 모든 경로를 캐치할 수 있음
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react_app(path):
        # API 경로는 제외
        if path.startswith('api/'):
            return jsonify({'error': 'Not found'}), 404
        
        # 정적 파일이 존재하면 서빙 (assets 등)
        if path and os.path.exists(static_folder_path):
            static_path = os.path.join(static_folder_path, path)
            # 실제 파일이 존재하는 경우만 서빙
            if os.path.exists(static_path) and os.path.isfile(static_path):
                return send_from_directory(static_folder_path, path)
        
        # SPA 라우팅을 위해 index.html 반환 (모든 경로에 대해)
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        
        # 빌드된 파일이 없으면 안내 메시지
        return jsonify({
            'error': 'Frontend not built',
            'message': 'Please run "cd frontend && npm run build" first'
        }), 503

    return app

