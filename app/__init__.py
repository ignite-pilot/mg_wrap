from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from app.utils.aws_secrets import get_postgres_info

load_dotenv()

db = SQLAlchemy()

def create_app():
    # Set static folder to frontend/dist for production
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'dist')

    if os.path.exists(static_folder):
        app = Flask(__name__, static_folder=static_folder, static_url_path='')
    else:
        app = Flask(__name__)

    # Configuration
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise ValueError(
            "SECRET_KEY must be set in .env file. "
            "Generate a secure random key for production use."
        )
    app.config['SECRET_KEY'] = secret_key
    
    # PostgreSQL 연결 설정 (AWS Secrets Manager에서 가져오기)
    postgres_info = get_postgres_info()
    if not postgres_info:
        raise ValueError(
            "Failed to retrieve PostgreSQL connection info from AWS Secrets Manager. "
            "Please check 'prod/ignite-pilot/postgresInfo2' secret."
        )
    
    # Secrets Manager에서 가져온 정보 사용
    db_user = postgres_info.get('user') or postgres_info.get('username') or postgres_info.get('DB_USER')
    db_password = postgres_info.get('password') or postgres_info.get('DB_PASSWORD')
    db_host = postgres_info.get('host') or postgres_info.get('hostname') or postgres_info.get('DB_HOST')
    db_port = postgres_info.get('port') or postgres_info.get('DB_PORT', '5432')
    # db_name은 ig-board로 고정
    db_name = 'ig-board'
    
    # 필수 값 검증
    if not all([db_user, db_password, db_host]):
        raise ValueError(
            "Missing required database connection info from AWS Secrets Manager. "
            "Required fields: user/username, password, host/hostname"
        )
    
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # CORS 설정 - 프로덕션에서는 특정 도메인만 허용해야 함
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:8400').split(',')
    # ig-member 프론트엔드도 허용 (OAuth 콜백을 위해)
    ig_member_frontend = os.getenv('IG_MEMBER_FRONTEND_URL', 'http://localhost:8200')
    if ig_member_frontend not in cors_origins:
        cors_origins.append(ig_member_frontend)
    
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

    # Serve React App (SPA fallback)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react_app(path):
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app

