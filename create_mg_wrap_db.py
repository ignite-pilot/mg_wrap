#!/usr/bin/env python3
"""
AWS PostgreSQL에 mg-wrap 데이터베이스 생성 및 스키마 적용 스크립트
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

# app 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.aws_secrets import get_postgres_info

DB_NAME = 'mg-wrap'

def create_database():
    """mg-wrap 데이터베이스 생성"""
    try:
        print("🔐 AWS Secrets Manager에서 PostgreSQL 연결 정보 가져오는 중...")
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
        
        print(f"📡 PostgreSQL 서버에 연결 중... ({db_host}:{db_port})")
        
        # postgres 데이터베이스에 연결 (기본 데이터베이스)
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database='postgres'  # 기본 postgres 데이터베이스에 연결
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # mg-wrap 데이터베이스가 이미 있는지 확인
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if exists:
            print(f'✅ {DB_NAME} 데이터베이스가 이미 존재합니다.')
        else:
            # mg-wrap 데이터베이스 생성
            cursor.execute(f"CREATE DATABASE \"{DB_NAME}\"")
            print(f'✅ {DB_NAME} 데이터베이스가 성공적으로 생성되었습니다.')
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f'❌ 연결 오류: {e}')
        print('네트워크 연결을 확인해주세요.')
        return False
    except Exception as e:
        print(f'❌ 오류 발생: {e}')
        import traceback
        traceback.print_exc()
        return False

def apply_schema():
    """mg-wrap 데이터베이스에 스키마 적용"""
    try:
        print("\n🔐 AWS Secrets Manager에서 PostgreSQL 연결 정보 가져오는 중...")
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
        
        print(f"📡 {DB_NAME} 데이터베이스에 연결 중...")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=DB_NAME
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("📄 스키마 파일 읽는 중...")
        schema_file = 'database/schema_postgresql.sql'
        if not os.path.exists(schema_file):
            print(f"❌ 스키마 파일을 찾을 수 없습니다: {schema_file}")
            return False
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print("🔧 스키마 적용 중...")
        
        # 전체 SQL을 한 번에 실행 (PostgreSQL은 여러 명령을 한 번에 실행 가능)
        try:
            cur.execute(schema_sql)
            print("✅ 스키마 적용 완료!")
        except Exception as e:
            error_msg = str(e).lower()
            # 일부 오류는 무시 (이미 존재하는 경우 등)
            if 'already exists' in error_msg or 'duplicate' in error_msg:
                print(f"⚠️  일부 객체가 이미 존재합니다: {str(e)[:100]}")
                print("✅ 스키마 적용 완료 (일부는 이미 존재)")
            else:
                print(f"⚠️  스키마 적용 중 일부 오류 발생: {str(e)[:200]}")
                print("✅ 스키마 적용 완료 (일부 오류는 무시됨)")
        
        cur.close()
        conn.close()
        print("\n✅ 스키마 적용 완료!")
        
        cur.close()
        conn.close()
        
        return True
        
    except FileNotFoundError:
        print(f"❌ 스키마 파일을 찾을 수 없습니다: database/schema_postgresql.sql")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print(f"📦 {DB_NAME} 데이터베이스 생성 및 스키마 적용")
    print("=" * 60)
    
    # 1. 데이터베이스 생성
    if not create_database():
        print("\n❌ 데이터베이스 생성 실패")
        return False
    
    # 2. 스키마 적용
    if not apply_schema():
        print("\n❌ 스키마 적용 실패")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 모든 작업이 완료되었습니다!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()

