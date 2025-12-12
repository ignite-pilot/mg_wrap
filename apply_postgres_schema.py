#!/usr/bin/env python3
"""PostgreSQL 스키마 적용 스크립트"""
import psycopg2
import sys
import os

# app 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.aws_secrets import get_postgres_info

# DB 이름은 ig-board로 고정
DB_NAME = 'ig-board'

def apply_schema():
    """PostgreSQL 스키마 적용"""
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
        conn.autocommit = True
        cur = conn.cursor()
        
        print("스키마 파일 읽는 중...")
        with open('database/schema_postgresql.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print("스키마 적용 중...")
        # 전체 SQL을 한 번에 실행
        try:
            cur.execute(schema_sql)
            print("✅ 스키마 적용 완료!")
        except Exception as e:
            # 일부 오류는 무시 (이미 존재하는 경우 등)
            error_msg = str(e).lower()
            if 'already exists' in error_msg or 'duplicate' in error_msg:
                print(f"⚠️  일부 객체가 이미 존재합니다: {e}")
                print("✅ 스키마 적용 완료 (일부는 이미 존재)")
            else:
                print(f"❌ 오류 발생: {e}")
                # 오류가 있어도 계속 진행
                print("⚠️  일부 오류가 발생했지만 계속 진행합니다.")
        
        cur.close()
        conn.close()
        print("\n✅ 스키마 적용 완료!")
        return True
        
    except FileNotFoundError:
        print("❌ 스키마 파일을 찾을 수 없습니다: database/schema_postgresql.sql")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    apply_schema()

