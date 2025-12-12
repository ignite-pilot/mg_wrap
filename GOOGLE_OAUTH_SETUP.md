# Google OAuth 설정 가이드

## 1. Google Cloud Console에서 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 상단의 프로젝트 선택 메뉴에서 "새 프로젝트" 클릭
3. 프로젝트 이름 입력 (예: "맡길랩 엔터프라이즈")
4. "만들기" 클릭

## 2. OAuth 동의 화면 구성

1. 왼쪽 메뉴에서 "API 및 서비스" > "OAuth 동의 화면" 선택
2. 사용자 유형 선택: "외부" 선택 후 "만들기"
3. 앱 정보 입력:
   - 앱 이름: "맡길랩 엔터프라이즈"
   - 사용자 지원 이메일: 본인 이메일
   - 개발자 연락처 정보: 본인 이메일
4. "저장 후 계속" 클릭
5. 범위는 기본값으로 두고 "저장 후 계속"
6. 테스트 사용자 추가 (선택사항): "저장 후 계속"
7. 요약 확인 후 "대시보드로 돌아가기"

## 3. OAuth 클라이언트 ID 생성

1. "API 및 서비스" > "사용자 인증 정보" 메뉴 선택
2. 상단의 "+ 사용자 인증 정보 만들기" > "OAuth 클라이언트 ID" 선택
3. 애플리케이션 유형: "웹 애플리케이션" 선택
4. 이름: "맡길랩 엔터프라이즈 웹 클라이언트" (또는 원하는 이름)
5. 승인된 JavaScript 원본:
   - `http://localhost:3000`
6. 승인된 리디렉션 URI:
   - `http://localhost:3000`
   - `http://localhost:5000` (필요시)
7. "만들기" 클릭
8. **클라이언트 ID를 복사** (중요!)

## 4. 환경 변수 설정

### Frontend 설정

`frontend/.env` 파일을 열고 다음을 추가:

```env
VITE_GOOGLE_CLIENT_ID=여기에_복사한_클라이언트_ID_붙여넣기
```

예시:
```env
VITE_GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
```

### Backend 설정 (선택사항)

백엔드에서도 Google 토큰 검증을 하려면 `루트/.env` 파일에 추가:

```env
GOOGLE_CLIENT_ID=여기에_같은_클라이언트_ID_붙여넣기
GOOGLE_CLIENT_SECRET=여기에_클라이언트_시크릿_붙여넣기
```

## 5. 서버 재시작

환경 변수를 변경한 후에는 서버를 재시작해야 합니다:

```bash
# Frontend 재시작
cd frontend
# Ctrl+C로 기존 프로세스 종료 후
npm run dev

# Backend 재시작 (필요시)
# Ctrl+C로 기존 프로세스 종료 후
python3 run.py
```

## 문제 해결

### "Missing required parameter: client_id" 오류
- `frontend/.env` 파일에 `VITE_GOOGLE_CLIENT_ID`가 제대로 설정되었는지 확인
- Vite는 환경 변수 변경 시 서버 재시작이 필요합니다
- `.env` 파일이 `frontend` 디렉토리에 있는지 확인

### "redirect_uri_mismatch" 오류
- Google Cloud Console에서 승인된 리디렉션 URI가 정확히 `http://localhost:3000`으로 설정되었는지 확인
- URI는 정확히 일치해야 합니다 (마지막 슬래시 포함 여부도 중요)

### 로그인 후 오류 발생
- 백엔드의 `.env` 파일에 `GOOGLE_CLIENT_ID`가 설정되었는지 확인
- 백엔드 서버가 실행 중인지 확인 (`http://localhost:5000`)

