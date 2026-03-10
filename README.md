# 맡길랩 엔터프라이즈 웹 서비스

맡길랩 엔터프라이즈는 기업을 위한 전문 짐 보관 서비스입니다.

## 기술 스택

### Backend
- Python 3.8+
- Flask
- PostgreSQL
- SQLAlchemy
- ig-member 서비스 (회원 관리)

### Frontend
- React 18
- Vite
- React Router
- Axios

## 설치 및 실행

### 1. 데이터베이스 설정

PostgreSQL 데이터베이스 연결 정보는 AWS Secrets Manager에서 가져옵니다:
- Secret Name: `prod/ignite-pilot/postgresInfo2`
- Database: `ig-board`

스키마를 적용합니다:

```bash
python apply_schema_properly.py
```

### 2. Backend 설정

```bash
# 가상환경 생성 (선택사항)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
# .env 파일을 생성하고 다음 변수들을 설정하세요:
# - SECRET_KEY: JWT 토큰 암호화를 위한 시크릿 키 (필수)
# - DB_USER: PostgreSQL 사용자 (기본값: postgres)
# - DB_PASSWORD: PostgreSQL 비밀번호 (필수)
# - DB_HOST: PostgreSQL 호스트 (필수)
# - DB_NAME: 데이터베이스 이름 (기본값: mg_wrap)
# - IG_MEMBER_API_URL: ig-member API URL (기본값: http://localhost:8201/api)
# - IG_BOARD_API_URL: ig-board API URL (기본값: http://localhost:8301)
# - CORS_ORIGINS: 허용된 CORS 출처 (기본값: http://localhost:8400)
```

### 3. Frontend 빌드

프론트엔드는 Flask가 서빙하므로 빌드가 필요합니다:

```bash
cd frontend
npm install
npm run build
```

빌드된 파일은 `frontend/dist`에 생성되며, Flask가 자동으로 서빙합니다.

### 4. 실행

**단일 서비스 실행 (Frontend + Backend 통합):**
```bash
# 프론트엔드 빌드 (최초 1회 또는 변경 시)
cd frontend
npm run build
cd ..

# 서비스 실행
python run.py
```

- 서비스 URL: http://localhost:8400
- API 엔드포인트: http://localhost:8400/api/*

## 필수 서비스

이 프로젝트는 다음 서비스들이 실행 중이어야 합니다:

### 1. ig-member 서비스 (회원 관리)
- Frontend: http://localhost:8200
- Backend: http://localhost:8201
- mg_wrap의 회원 관리는 ig-member 서비스를 통해 처리됩니다.

### 2. ig-board 서비스 (게시판, 선택사항)
- Frontend: http://localhost:8300
- Backend: http://localhost:8301
- 문의하기 게시판 기능 사용 시 필요합니다.

## 주요 기능

- **회원 관리**: ig-member 서비스를 통한 회원가입/로그인 (Google OAuth, 이메일 회원가입 지원)
- **보관 신청**: 공간형/BOX형 자산보관 신청 및 견적 조회
- **보관 자산 관리**: 자산 등록, 엑셀 업로드, 회수/폐기 신청
- **회수 현황**: 회수 신청 목록 및 상태 관리
- **폐기 현황**: 폐기 신청 목록 및 상태 관리
- **문의하기 게시판**: ig-board 서비스를 통한 게시판 기능 (선택사항)

## 가격 정책

### 공간형 자산보관 (5평 기준)
- 1개월: 300,000원
- 3개월: 800,000원
- 6개월: 1,500,000원

### BOX형 자산보관 (BOX 1개 기준)
- 1개월: 30,000원
- 3개월: 80,000원
- 6개월: 150,000원

## 프로젝트 구조

```
mg_wrap/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── utils.py
│   ├── services/
│   │   └── member_service.py  # ig-member API 클라이언트
│   └── routes/
│       ├── auth.py            # ig-member API 사용
│       ├── storage.py
│       ├── assets.py
│       ├── retrieval.py
│       ├── disposal.py
│       └── board.py           # ig-board 연동
├── database/
│   ├── schema_postgresql.sql
│   └── migration_remove_user_foreign_key.sql
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/
│   │   └── services/
│   └── package.json
├── tests/
│   └── test_*.py
├── requirements.txt
├── run.py
├── run_tests_and_security.py  # 자동 테스트 및 보안 체크
└── README.md
```

## 개발 가이드

- Database: PostgreSQL (AWS RDS)
- GitHub: https://github.com/marojun/mg-wrap-enterprise.git
- 회원 관리: ig-member 서비스 사용
- 게시판: ig-board 서비스 사용 (선택사항)

## 관련 문서

- [IG_MEMBER_MIGRATION.md](./IG_MEMBER_MIGRATION.md) - ig-member 전환 가이드
- [SECURITY.md](./SECURITY.md) - 보안 가이드
- [AUTO_TEST_GUIDE.md](./AUTO_TEST_GUIDE.md) - 자동 테스트 가이드
- [Requirement.md](./Requirement.md) - 요구사항 및 포트 정보

