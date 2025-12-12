-- 맡길랩 엔터프라이즈 데이터베이스 스키마 (PostgreSQL)

-- ENUM 타입 생성
CREATE TYPE storage_type_enum AS ENUM ('space', 'box');
CREATE TYPE application_status_enum AS ENUM ('pending', 'approved', 'active', 'completed');
CREATE TYPE asset_category_enum AS ENUM ('office_supplies', 'documents', 'equipment', 'furniture', 'clothing', 'appliances', 'other');
CREATE TYPE asset_status_enum AS ENUM ('stored', 'retrieval_requested', 'retrieval_cancelled', 'retrieved', 'disposal_requested', 'disposal_cancelled', 'disposed');
CREATE TYPE retrieval_status_enum AS ENUM ('preparing', 'in_transit', 'completed', 'cancelled');
CREATE TYPE disposal_status_enum AS ENUM ('preparing', 'completed', 'cancelled');

-- 사용자 테이블 제거됨 - ig-member 서비스를 사용
-- user_id는 ig-member의 사용자 ID를 저장하는 단순 정수 필드

-- updated_at 자동 업데이트 함수 생성
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 보관 신청 테이블
CREATE TABLE IF NOT EXISTS storage_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    storage_type storage_type_enum NOT NULL,
    space_pyeong INTEGER DEFAULT NULL,
    box_count INTEGER DEFAULT NULL,
    months INTEGER NOT NULL,
    estimated_price NUMERIC(12, 2) NOT NULL,
    status application_status_enum DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- 외래키 제약조건 제거됨 - ig-member 서비스 사용으로 users 테이블 제거
    -- user_id는 ig-member의 사용자 ID를 저장
);

CREATE INDEX IF NOT EXISTS idx_storage_applications_user_id ON storage_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_storage_applications_status ON storage_applications(status);

-- updated_at 트리거 생성
CREATE TRIGGER update_storage_applications_updated_at BEFORE UPDATE ON storage_applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 보관 자산 테이블
CREATE TABLE IF NOT EXISTS assets (
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
);

CREATE INDEX IF NOT EXISTS idx_assets_storage_application_id ON assets(storage_application_id);
CREATE INDEX IF NOT EXISTS idx_assets_asset_number ON assets(asset_number);
CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);
CREATE INDEX IF NOT EXISTS idx_assets_asset_category ON assets(asset_category);

-- updated_at 트리거 생성
CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 회수 현황 테이블
CREATE TABLE IF NOT EXISTS retrieval_requests (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL,
    status retrieval_status_enum DEFAULT 'preparing',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_retrieval_requests_asset_id ON retrieval_requests(asset_id);
CREATE INDEX IF NOT EXISTS idx_retrieval_requests_status ON retrieval_requests(status);

-- updated_at 트리거 생성
CREATE TRIGGER update_retrieval_requests_updated_at BEFORE UPDATE ON retrieval_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 폐기 현황 테이블
CREATE TABLE IF NOT EXISTS disposal_requests (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL,
    status disposal_status_enum DEFAULT 'preparing',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_disposal_requests_asset_id ON disposal_requests(asset_id);
CREATE INDEX IF NOT EXISTS idx_disposal_requests_status ON disposal_requests(status);

-- updated_at 트리거 생성
CREATE TRIGGER update_disposal_requests_updated_at BEFORE UPDATE ON disposal_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

