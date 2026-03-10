#!/usr/bin/env python3
"""PostgreSQL 테이블 확인 스크립트"""
import psycopg2
import sys
import os

# app 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.aws_secrets import get_postgres_info

# DB 이름은 mg-wrap로 고정
DB_NAME = 'mg-wrap'

def check_tables():
    """테이블 목록 확인"""
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
        
        print("PostgreSQL에 연결 중...")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=DB_NAME
        )
        cur = conn.cursor()
        
        # 테이블 목록 조회
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        print(f"\n📋 현재 데이터베이스 '{DB_NAME}'의 테이블 목록:")
        if tables:
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("  ❌ 테이블이 없습니다!")
        
        # ENUM 타입 확인
        cur.execute("""
            SELECT typname 
            FROM pg_type 
            WHERE typtype = 'e'
            ORDER BY typname;
        """)
        enums = cur.fetchall()
        
        print("\n📋 ENUM 타입 목록:")
        if enums:
            for enum in enums:
                print(f"  - {enum[0]}")
        else:
            print("  ❌ ENUM 타입이 없습니다!")
        
        cur.close()
        conn.close()
        return len(tables) > 0
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    check_tables()

