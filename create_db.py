#!/usr/bin/env python3
"""
AWS PostgreSQL에 mg_wrap 데이터베이스 생성 스크립트
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 데이터베이스 연결 정보
DB_CONFIG = {
    'host': 'resume-ai-pgvector-dev.crkgaskg6o61.ap-northeast-2.rds.amazonaws.com',
    'port': 5432,
    'user': 'postgres',
    'password': '?bV8tZr65x.WSYt_',
    'database': 'postgres'  # 기본 postgres 데이터베이스에 연결
}

def create_database():
    """mg_wrap 데이터베이스 생성"""
    try:
        # postgres 데이터베이스에 연결 (기본 데이터베이스)
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # mg_wrap 데이터베이스가 이미 있는지 확인
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'mg_wrap'")
        exists = cursor.fetchone()
        
        if exists:
            print('✓ mg_wrap 데이터베이스가 이미 존재합니다.')
        else:
            # mg_wrap 데이터베이스 생성
            cursor.execute('CREATE DATABASE mg_wrap')
            print('✓ mg_wrap 데이터베이스가 성공적으로 생성되었습니다.')
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f'✗ 연결 오류: {e}')
        print('네트워크 연결을 확인해주세요.')
        return False
    except Exception as e:
        print(f'✗ 오류 발생: {e}')
        return False

if __name__ == '__main__':
    print('AWS PostgreSQL에 연결하여 mg_wrap 데이터베이스를 생성합니다...')
    create_database()

