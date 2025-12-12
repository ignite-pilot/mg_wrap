# 맡길랩 엔터프라이즈 설정 가이드

## 빠른 시작

### 1. 데이터베이스 준비

```bash
# MySQL 접속
mysql -u root -p

# 데이터베이스 생성
CREATE DATABASE mg_wrap CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;

# 스키마 적용
mysql -u root -p mg_wrap < database/schema.sql
```

### 2. Backend 설정

```bash
# Python 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# .env 파일 생성 (루트 디렉토리에)
# 주의: DB 연결 정보는 AWS Secrets Manager에서 자동으로 가져옵니다.
cat > .env << EOF
SECRET_KEY=your_secret_key_here_change_in_production
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
FLASK_ENV=development
FLASK_DEBUG=True
EOF

# 데이터베이스 테이블 생성
python init_db.py

# 서버 실행
python run.py
```

### 3. Frontend 설정

```bash
cd frontend

# 의존성 설치
npm install

# .env 파일 생성 (선택사항)
cat > .env << EOF
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
EOF

# 개발 서버 실행
npm run dev
```

## Google OAuth 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. "API 및 서비스" > "사용자 인증 정보" 이동
4. "사용자 인증 정보 만들기" > "OAuth 클라이언트 ID" 선택
5. 애플리케이션 유형: "웹 애플리케이션"
6. 승인된 리디렉션 URI 추가:
   - `http://localhost:3000`
   - `http://localhost:5000` (필요시)
7. 클라이언트 ID와 클라이언트 시크릿을 복사하여 `.env` 파일에 설정

## 접속 정보

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Database: localhost:3306 (MySQL)

## 문제 해결

### 데이터베이스 연결 오류
- MySQL이 실행 중인지 확인
- 데이터베이스 이름과 사용자 정보가 올바른지 확인
- `.env` 파일의 DB 설정 확인

### Google OAuth 오류
- Google Cloud Console에서 클라이언트 ID가 올바른지 확인
- 승인된 리디렉션 URI가 정확히 설정되었는지 확인
- `.env` 파일의 `GOOGLE_CLIENT_ID` 확인

### 프론트엔드 빌드 오류
- Node.js 버전 확인 (권장: 16 이상)
- `node_modules` 삭제 후 `npm install` 재실행

