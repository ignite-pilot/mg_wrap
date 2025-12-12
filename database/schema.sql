-- 맡길랩 엔터프라이즈 데이터베이스 스키마

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_google_id (google_id),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 보관 신청 테이블
CREATE TABLE IF NOT EXISTS storage_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    storage_type ENUM('space', 'box') NOT NULL COMMENT '공간형 또는 BOX형',
    space_pyeong INT DEFAULT NULL COMMENT '공간형인 경우 평수',
    box_count INT DEFAULT NULL COMMENT 'BOX형인 경우 BOX 수량',
    months INT NOT NULL COMMENT '보관 개월수',
    estimated_price DECIMAL(12, 2) NOT NULL COMMENT '견적 금액',
    status ENUM('pending', 'approved', 'active', 'completed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 보관 자산 테이블
CREATE TABLE IF NOT EXISTS assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_number VARCHAR(50) UNIQUE NOT NULL COMMENT '자산번호 (시스템 자동 부여)',
    storage_application_id INT NOT NULL,
    application_date DATE NOT NULL COMMENT '보관 신청일',
    storage_start_date DATE NULL COMMENT '보관 시작일',
    asset_category ENUM('office_supplies', 'documents', 'equipment', 'furniture', 'clothing', 'appliances', 'other') NOT NULL COMMENT '자산 분류',
    special_notes TEXT COMMENT '특이사항',
    status ENUM('stored', 'retrieval_requested', 'retrieval_cancelled', 'retrieved', 'disposal_requested', 'disposal_cancelled', 'disposed') DEFAULT 'stored',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (storage_application_id) REFERENCES storage_applications(id) ON DELETE CASCADE,
    INDEX idx_storage_application_id (storage_application_id),
    INDEX idx_asset_number (asset_number),
    INDEX idx_status (status),
    INDEX idx_asset_category (asset_category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 회수 현황 테이블
CREATE TABLE IF NOT EXISTS retrieval_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    status ENUM('preparing', 'in_transit', 'completed', 'cancelled') DEFAULT 'preparing' COMMENT '출고 준비중, 출고중, 회수 완료, 취소',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    INDEX idx_asset_id (asset_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 폐기 현황 테이블
CREATE TABLE IF NOT EXISTS disposal_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    status ENUM('preparing', 'completed', 'cancelled') DEFAULT 'preparing' COMMENT '폐기 준비중, 폐기 완료, 취소',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    INDEX idx_asset_id (asset_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

