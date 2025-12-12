-- 보관 시작일을 NULL 허용으로 변경하는 마이그레이션
ALTER TABLE assets MODIFY COLUMN storage_start_date DATE NULL;

