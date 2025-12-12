#!/usr/bin/env python3
"""PostgreSQL 연결 테스트 스크립트"""
import psycopg2
import sys
import os

# app 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.aws_secrets import get_postgres_info

# DB 이름은 ig-board로 고정
DB_NAME = 'ig-board'

def test_connection():
    """PostgreSQL 연결 테스트"""
    try:
        print("AWS Secrets Manager에서 PostgreSQL 연결 정보 가져오는 중...")
        postgres_info = get_postgres_info()
        
        if not postgres_info:
            print("❌ AWS Secrets Manager에서 PostgreSQL 정보를 가져올 수 없습니다.")
            return False
        
        # Secrets Manager에서 가져온 정보 사용
        db_host = postgres_info.get('host') or postgres_info.get('hostname') or postgres_info.get('DB_HOST')
        db_port = postgres_info.get('port') or postgres_info.get('DB_PORT', '5432')
        db_user = postgres_info.get('user') or postgres_info.get('username') or postgres_info.get('DB_USER')
        db_password = postgres_info.get('password') or postgres_info.get('DB_PASSWORD')
        
        if not all([db_host, db_user, db_password]):
            print("❌ 필수 데이터베이스 연결 정보가 없습니다.")
            return False
        
        print("PostgreSQL에 연결 시도 중...")
        print(f"Host: {db_host}")
        print(f"Port: {db_port}")
        print(f"Database: {DB_NAME}")
        print(f"User: {db_user}")
        
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=DB_NAME
        )
        
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print("\n✅ 연결 성공!")
        print(f"PostgreSQL 버전: {version[0]}")
        
        # 데이터베이스 목록 확인
        cur.execute("SELECT current_database();")
        current_db = cur.fetchone()
        print(f"현재 데이터베이스: {current_db[0]}")
        
        cur.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ 연결 실패: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    test_connection()
