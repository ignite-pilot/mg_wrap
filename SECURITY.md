# 보안 가이드

## 환경 변수 설정

프로덕션 환경에서는 반드시 `.env` 파일에 다음 환경 변수를 설정해야 합니다:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration (PostgreSQL)
DB_HOST=your-database-host
DB_PORT=5432
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_NAME=mg_wrap

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# CORS Configuration (comma-separated list of allowed origins)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ig-board Integration
IG_BOARD_API_URL=http://localhost:8301
INQUIRY_BOARD_ID=2
IG_BOARD_SECRET_KEY=your-ig-board-secret-key
IG_BOARD_ALGORITHM=HS256
```

## 보안 체크리스트

### ✅ 완료된 보안 개선 사항

1. **하드코딩된 비밀번호 제거**
   - 데이터베이스 비밀번호를 환경 변수로 이동
   - SECRET_KEY를 환경 변수로 이동
   - 필수 환경 변수 검증 추가

2. **CORS 설정 제한**
   - 모든 출처 허용(`*`) 제거
   - 환경 변수로 허용된 출처 설정 가능
   - 프로덕션에서는 특정 도메인만 허용

3. **에러 메시지 보안**
   - 민감한 정보(스택 트레이스, 상세 에러)를 클라이언트에 노출하지 않음
   - 로그에는 상세 정보 기록, 클라이언트에는 일반 메시지만 반환

4. **에러 처리 개선**
   - 공통 에러 핸들러(`app/utils.py`) 추가
   - 모든 라우트에서 일관된 에러 처리

### ⚠️ 추가 권장 사항

1. **환경 변수 관리**
   - `.env` 파일을 `.gitignore`에 추가 (이미 추가되어 있어야 함)
   - 프로덕션에서는 환경 변수 관리 시스템 사용 (AWS Secrets Manager, HashiCorp Vault 등)

2. **HTTPS 사용**
   - 프로덕션에서는 반드시 HTTPS 사용
   - SSL/TLS 인증서 설정

3. **Rate Limiting**
   - API 엔드포인트에 Rate Limiting 추가 고려
   - Flask-Limiter 사용 권장

4. **입력 검증 강화**
   - 모든 사용자 입력에 대한 검증
   - SQL Injection 방지 (SQLAlchemy ORM 사용으로 이미 방지됨)
   - XSS 방지 (프론트엔드에서 처리)

5. **인증/인가**
   - JWT 토큰 만료 시간 적절히 설정 (현재 7일)
   - Refresh Token 구현 고려
   - 권한 기반 접근 제어 (RBAC) 구현 고려

6. **로깅 및 모니터링**
   - 보안 이벤트 로깅
   - 이상 행위 감지
   - 로그 분석 도구 사용

7. **의존성 보안**
   - 정기적으로 `pip audit` 또는 `safety check` 실행
   - 취약점이 있는 패키지 업데이트

## 보안 테스트

다음 명령어로 보안 취약점을 확인할 수 있습니다:

```bash
# Python 패키지 취약점 검사
pip install safety
safety check

# 또는 pip-audit 사용
pip install pip-audit
pip-audit
```

## 비상 대응

보안 사고 발생 시:

1. 즉시 영향받는 시스템 격리
2. 로그 확인 및 분석
3. 취약점 패치 적용
4. 사용자에게 알림 (필요시)
5. 사고 보고서 작성

