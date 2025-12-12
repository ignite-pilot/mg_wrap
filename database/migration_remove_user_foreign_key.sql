-- users 테이블 외래키 제약조건 제거 마이그레이션
-- ig-member 서비스로 전환하면서 users 테이블을 제거하고 외래키 제약조건도 제거

-- storage_applications 테이블의 외래키 제약조건 제거
ALTER TABLE storage_applications 
DROP CONSTRAINT IF EXISTS storage_applications_user_id_fkey;

-- users 테이블 제거 (데이터 백업 필요 시 먼저 백업)
-- DROP TABLE IF EXISTS users CASCADE;

-- 참고: user_id는 이제 ig-member의 사용자 ID를 저장하는 단순 정수 필드입니다.
-- 외래키 제약조건이 없으므로 ig-member의 사용자 ID를 직접 저장할 수 있습니다.

