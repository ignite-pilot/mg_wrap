#!/usr/bin/env python3
"""PostgreSQL 스키마 올바르게 적용 스크립트"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

# app 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.aws_secrets import get_postgres_info

# DB 이름은 mg-wrap로 고정
DB_NAME = 'mg-wrap'

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
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("스키마 파일 읽는 중...")
        with open('database/schema_postgresql.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print("스키마 적용 중...")
        
        # SQL을 실행 가능한 단위로 분리
        # 세미콜론으로 분리하되, 함수 정의 내부의 세미콜론은 제외
        statements = []
        current_statement = ""
        dollar_quote = None
        
        for line in schema_sql.split('\n'):
            line = line.strip()
            if not line or line.startswith('--'):
                continue
            
            # Dollar quoting 체크 (함수 정의)
            if '$$' in line:
                if dollar_quote is None:
                    # 시작
                    dollar_quote = line.split('$$')[1] if '$$' in line else None
                elif dollar_quote in line:
                    # 종료
                    dollar_quote = None
            
            current_statement += line + '\n'
            
            # Dollar quoting이 끝나고 세미콜론이 있으면 명령 완료
            if dollar_quote is None and line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
        
        # 마지막 명령 처리
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        # 각 명령 실행
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue
            try:
                cur.execute(statement)
                print(f"✅ [{i}/{len(statements)}] 실행 완료")
            except Exception as e:
                error_msg = str(e).lower()
                if 'already exists' in error_msg or 'duplicate' in error_msg:
                    print(f"⚠️  [{i}/{len(statements)}] 이미 존재: {str(e)[:80]}")
                else:
                    print(f"❌ [{i}/{len(statements)}] 오류: {str(e)[:100]}")
                    print(f"   명령: {statement[:100]}...")
        
        cur.close()
        conn.close()
        print("\n✅ 스키마 적용 완료!")
        return True
        
    except FileNotFoundError:
        print("❌ 스키마 파일을 찾을 수 없습니다: database/schema_postgresql.sql")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    apply_schema()

