"""관리자 API 엔드포인트"""
from flask import Blueprint, jsonify
import os
import psycopg2

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def get_db_connection():
    """PostgreSQL 데이터베이스 연결 생성"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )


@admin_bp.route('/init-db', methods=['POST'])
def init_database():
    """데이터베이스 스키마 초기화"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # PostgreSQL 스키마 파일 읽기
        schema_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'database',
            'schema_postgresql.sql'
        )

        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # 스키마 적용
        cur.execute(schema_sql)
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Database schema initialized successfully'
        }), 200

    except Exception as e:
        error_msg = str(e).lower()
        # 이미 존재하는 경우는 성공으로 처리
        if 'already exists' in error_msg or 'duplicate' in error_msg:
            return jsonify({
                'status': 'success',
                'message': 'Database schema already exists',
                'detail': str(e)
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'Failed to initialize database: {str(e)}'
            }), 500


@admin_bp.route('/db-status', methods=['GET'])
def db_status():
    """데이터베이스 연결 상태 및 테이블 확인"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 테이블 목록 조회
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]

        # ENUM 타입 조회
        cur.execute("""
            SELECT typname
            FROM pg_type
            WHERE typtype = 'e'
            ORDER BY typname
        """)
        enums = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'connection': 'ok',
            'tables': tables,
            'enums': enums,
            'table_count': len(tables),
            'enum_count': len(enums)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'connection': 'failed',
            'message': str(e)
        }), 500
