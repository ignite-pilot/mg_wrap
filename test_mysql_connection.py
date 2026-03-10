#!/usr/bin/env python3
"""MySQL 연결 테스트 스크립트"""
import pymysql
import sys
import os

# app 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.aws_secrets import get_mysql_info

# DB 이름은 ig-board로 고정
DB_NAME = 'ig-board'

def test_connection():
    """MySQL 연결 테스트"""
    try:
        print("AWS Secrets Manager에서 MySQL 연결 정보 가져오는 중...")
        mysql_info = get_mysql_info()
        
        if not mysql_info:
            print("❌ AWS Secrets Manager에서 MySQL 정보를 가져올 수 없습니다.")
            return False
        
        # Secrets Manager에서 가져온 정보 사용
        db_host = mysql_info.get('host') or mysql_info.get('hostname') or mysql_info.get('DB_HOST')
        db_port = int(mysql_info.get('port') or mysql_info.get('DB_PORT', '3306'))
        db_user = mysql_info.get('user') or mysql_info.get('username') or mysql_info.get('DB_USER')
        db_password = mysql_info.get('password') or mysql_info.get('DB_PASSWORD')
        
        if not all([db_host, db_user, db_password]):
            print("❌ 필수 데이터베이스 연결 정보가 없습니다.")
            return False
        
        print("MySQL에 연결 시도 중...")
        print(f"Host: {db_host}")
        print(f"Port: {db_port}")
        print(f"Database: {DB_NAME}")
        print(f"User: {db_user}")
        
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=DB_NAME,
            charset='utf8mb4'
        )
        
        cur = conn.cursor()
        cur.execute("SELECT VERSION();")
        version = cur.fetchone()
        print("\n✅ 연결 성공!")
        print(f"MySQL 버전: {version[0]}")
        
        # 데이터베이스 목록 확인
        cur.execute("SELECT DATABASE();")
        current_db = cur.fetchone()
        print(f"현재 데이터베이스: {current_db[0]}")
        
        # 테이블 목록 확인
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        if tables:
            print(f"\n테이블 목록 ({len(tables)}개):")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("\n⚠️  테이블이 없습니다. 스키마를 초기화해야 합니다.")
        
        cur.close()
        conn.close()
        return True
        
    except pymysql.Error as e:
        print(f"\n❌ 연결 실패: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
