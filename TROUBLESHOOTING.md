# 문제 해결 가이드

## Google 로그인 500 에러 해결

### 1. 백엔드 서버 재시작
```bash
# 기존 서버 종료
pkill -f "python.*run.py"

# 서버 재시작
python3 run.py
```

### 2. 에러 로그 확인
백엔드 서버 콘솔에서 상세한 에러 메시지를 확인할 수 있습니다.
개선된 에러 로깅이 적용되어 더 자세한 정보를 제공합니다.

### 3. 데이터베이스 연결 확인
```bash
python3 test_postgres_connection.py
```

### 4. 환경 변수 확인
`.env` 파일에 다음이 설정되어 있는지 확인:
- `GOOGLE_CLIENT_ID`
- `DB_HOST`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

### 5. PostgreSQL 테이블 확인
```bash
python3 check_tables.py
```

### 6. 일반적인 원인
1. **데이터베이스 연결 실패**: 네트워크 문제 또는 자격 증명 오류
2. **테이블 누락**: 스키마가 제대로 적용되지 않음
3. **ENUM 타입 불일치**: PostgreSQL ENUM과 SQLAlchemy Enum 매핑 문제
4. **세션 관리 문제**: 데이터베이스 세션이 제대로 닫히지 않음

