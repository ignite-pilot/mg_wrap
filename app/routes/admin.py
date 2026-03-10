"""관리자 API 엔드포인트"""
from flask import Blueprint, jsonify
import os
import pymysql
from app.utils.aws_secrets import get_mysql_info

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def get_db_connection():
    """MySQL 데이터베이스 연결 생성"""
    mysql_info = get_mysql_info()
    if not mysql_info:
        raise ValueError("Failed to retrieve MySQL connection info from AWS Secrets Manager")
    
    db_user = mysql_info.get('user') or mysql_info.get('username') or mysql_info.get('DB_USER')
    db_password = mysql_info.get('password') or mysql_info.get('DB_PASSWORD')
    db_host = mysql_info.get('host') or mysql_info.get('hostname') or mysql_info.get('DB_HOST')
    db_port = int(mysql_info.get('port') or mysql_info.get('DB_PORT', '3306'))
    db_name = 'ig-board'
    
    return pymysql.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


@admin_bp.route('/init-db', methods=['POST'])
def init_database():
    """데이터베이스 스키마 초기화"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # MySQL 스키마 파일 읽기 (SQLAlchemy ORM 사용으로 스키마 파일은 참고용)
        # 실제로는 SQLAlchemy의 db.create_all()을 사용하는 것을 권장합니다.
        schema_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'database',
            'schema_postgresql.sql'
        )

        # MySQL은 PostgreSQL 스키마 파일을 직접 사용할 수 없으므로
        # SQLAlchemy ORM을 사용하여 테이블을 생성하는 것을 권장합니다.
        return jsonify({
            'status': 'info',
            'message': 'Please use SQLAlchemy db.create_all() to initialize database schema for MySQL',
            'note': 'MySQL schema should be created using SQLAlchemy ORM models'
        }), 200

    except Exception as e:
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

        # 테이블 목록 조회 (MySQL)
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            ORDER BY table_name
        """)
        tables = [row['table_name'] for row in cur.fetchall()]

        # MySQL에서는 ENUM 타입이 컬럼 정의에 포함되므로 별도 조회 불필요
        # 대신 테이블의 ENUM 컬럼을 조회
        enum_columns = []
        for table in tables:
            cur.execute("""
                SELECT column_name, column_type
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                AND table_name = %s
                AND column_type LIKE 'enum%'
            """, (table,))
            enum_columns.extend([f"{table}.{row['column_name']}" for row in cur.fetchall()])

        cur.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'connection': 'ok',
            'tables': tables,
            'enum_columns': enum_columns,
            'table_count': len(tables),
            'enum_column_count': len(enum_columns)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'connection': 'failed',
            'message': str(e)
        }), 500
