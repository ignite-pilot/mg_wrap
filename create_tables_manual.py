#!/usr/bin/env python3
"""mg-wrap 데이터베이스에 테이블 수동 생성"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.utils.aws_secrets import get_postgres_info

DB_NAME = 'mg-wrap'

def create_tables():
    """테이블 생성"""
    postgres_info = get_postgres_info()
    db_host = postgres_info.get('host') or postgres_info.get('hostname')
    db_port = postgres_info.get('port', '5432')
    db_user = postgres_info.get('user') or postgres_info.get('username')
    db_password = postgres_info.get('password')
    
    conn = psycopg2.connect(host=db_host, port=db_port, user=db_user, password=db_password, database=DB_NAME)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # 함수 생성
    func_sql = """CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';"""
    
    try:
        cur.execute(func_sql)
        print("✅ 함수 생성 완료")
    except Exception as e:
        print(f"⚠️  함수: {str(e)[:80]}")
    
    # 테이블 생성
    tables = [
        """CREATE TABLE IF NOT EXISTS storage_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    storage_type storage_type_enum NOT NULL,
    space_pyeong INTEGER DEFAULT NULL,
    box_count INTEGER DEFAULT NULL,
    months INTEGER NOT NULL,
    estimated_price NUMERIC(12, 2) NOT NULL,
    status application_status_enum DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
        """CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    asset_number VARCHAR(50) UNIQUE NOT NULL,
    storage_application_id INTEGER NOT NULL,
    application_date DATE NOT NULL,
    storage_start_date DATE NULL,
    asset_category asset_category_enum NOT NULL,
    special_notes TEXT,
    status asset_status_enum DEFAULT 'stored',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (storage_application_id) REFERENCES storage_applications(id) ON DELETE CASCADE
);""",
        """CREATE TABLE IF NOT EXISTS retrieval_requests (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL,
    status retrieval_status_enum DEFAULT 'preparing',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);""",
        """CREATE TABLE IF NOT EXISTS disposal_requests (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL,
    status disposal_status_enum DEFAULT 'preparing',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);"""
    ]
    
    for i, table_sql in enumerate(tables, 1):
        try:
            cur.execute(table_sql)
            print(f"✅ [{i}/{len(tables)}] 테이블 생성 완료")
        except Exception as e:
            print(f"⚠️  [{i}/{len(tables)}] 테이블 생성: {str(e)[:100]}")
    
    # 인덱스 생성
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_storage_applications_user_id ON storage_applications(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_storage_applications_status ON storage_applications(status);",
        "CREATE INDEX IF NOT EXISTS idx_assets_storage_application_id ON assets(storage_application_id);",
        "CREATE INDEX IF NOT EXISTS idx_assets_asset_number ON assets(asset_number);",
        "CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);",
        "CREATE INDEX IF NOT EXISTS idx_assets_asset_category ON assets(asset_category);",
        "CREATE INDEX IF NOT EXISTS idx_retrieval_requests_asset_id ON retrieval_requests(asset_id);",
        "CREATE INDEX IF NOT EXISTS idx_retrieval_requests_status ON retrieval_requests(status);",
        "CREATE INDEX IF NOT EXISTS idx_disposal_requests_asset_id ON disposal_requests(asset_id);",
        "CREATE INDEX IF NOT EXISTS idx_disposal_requests_status ON disposal_requests(status);"
    ]
    
    for idx_sql in indexes:
        try:
            cur.execute(idx_sql)
        except Exception as e:
            print(f"⚠️  인덱스 생성: {str(e)[:80]}")
    
    # 트리거 생성
    triggers = [
        "CREATE TRIGGER update_storage_applications_updated_at BEFORE UPDATE ON storage_applications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();",
        "CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON assets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();",
        "CREATE TRIGGER update_retrieval_requests_updated_at BEFORE UPDATE ON retrieval_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();",
        "CREATE TRIGGER update_disposal_requests_updated_at BEFORE UPDATE ON disposal_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();"
    ]
    
    for trigger_sql in triggers:
        try:
            cur.execute(trigger_sql)
        except Exception as e:
            print(f"⚠️  트리거 생성: {str(e)[:80]}")
    
    cur.close()
    conn.close()
    print("\n✅ 모든 테이블 생성 완료!")

if __name__ == "__main__":
    create_tables()

