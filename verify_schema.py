#!/usr/bin/env python3
"""PostgreSQL 스키마 상세 확인 스크립트"""
import psycopg2
import sys
import os

# app 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.aws_secrets import get_postgres_info

# DB 이름은 ig-board로 고정
DB_NAME = 'ig-board'

def verify_schema():
    """스키마 상세 확인"""
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
        
        print(f"\n📋 테이블 목록 ({len(tables)}개):")
        expected_tables = ['users', 'storage_applications', 'assets', 'retrieval_requests', 'disposal_requests']
        for table in tables:
            table_name = table[0]
            status = "✅" if table_name in expected_tables else "⚠️"
            print(f"  {status} {table_name}")
        
        # 각 테이블의 컬럼 확인
        for table in tables:
            table_name = table[0]
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)
            columns = cur.fetchall()
            print(f"\n  📊 {table_name} 테이블 컬럼:")
            for col in columns:
                nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                print(f"    - {col[0]}: {col[1]} ({nullable})")
        
        # 인덱스 확인
        cur.execute("""
            SELECT tablename, indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname;
        """)
        indexes = cur.fetchall()
        print(f"\n📋 인덱스 목록 ({len(indexes)}개):")
        for idx in indexes:
            print(f"  - {idx[0]}.{idx[1]}")
        
        # 트리거 확인
        cur.execute("""
            SELECT trigger_name, event_object_table
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
            ORDER BY event_object_table, trigger_name;
        """)
        triggers = cur.fetchall()
        print(f"\n📋 트리거 목록 ({len(triggers)}개):")
        for trigger in triggers:
            print(f"  - {trigger[1]}.{trigger[0]}")
        
        cur.close()
        conn.close()
        
        if len(tables) >= 5:
            print("\n✅ 모든 테이블이 정상적으로 생성되었습니다!")
            return True
        else:
            print(f"\n⚠️  일부 테이블이 누락되었습니다. (예상: 5개, 실제: {len(tables)}개)")
            return False
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_schema()

