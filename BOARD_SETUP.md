# 게시판 연동 설정 가이드

## 문제

게시글 작성 실패 원인: mg_wrap과 ig-board의 인증 시스템이 분리되어 있어, mg_wrap 사용자가 ig-board에 인증되지 않습니다.

## 해결 방법

### 1. ig-board에 사용자 등록

mg_wrap에 로그인한 사용자가 ig-board에도 동일한 Google 계정으로 로그인하여 등록되어 있어야 합니다.

**단계:**
1. ig-board 프론트엔드에 접속: `http://localhost:8300` (또는 ig-board 프론트엔드 URL)
2. 동일한 Google 계정으로 로그인
3. 이제 mg_wrap에서 해당 사용자로 게시글을 작성할 수 있습니다

### 2. 환경 변수 설정

백엔드 `.env` 파일에 다음 환경 변수를 추가하세요:

```env
# ig-board API 설정
IG_BOARD_API_URL=http://localhost:8301
INQUIRY_BOARD_ID=2

# ig-board 인증 설정 (토큰 생성용)
IG_BOARD_SECRET_KEY=your-secret-key-change-in-production
IG_BOARD_ALGORITHM=HS256
```

**중요:** `IG_BOARD_SECRET_KEY`는 ig-board 백엔드의 `.env` 파일에 있는 `SECRET_KEY`와 동일해야 합니다.

### 3. ig-board SECRET_KEY 확인

ig-board 프로젝트의 `.env` 파일을 확인하세요:

```bash
cd /Users/ignite/Documents/AI\ Coding/cursor_project/ig-board/backend
cat .env | grep SECRET_KEY
```

해당 값을 mg_wrap의 `.env` 파일에 `IG_BOARD_SECRET_KEY`로 설정하세요.

### 4. 게시판 생성

ig-board에 "문의하기" 게시판을 생성하고, 해당 게시판 ID를 `INQUIRY_BOARD_ID`에 설정하세요.

**게시판 생성 방법:**
1. ig-board 관리자로 로그인
2. 게시판 생성 페이지에서 "문의하기" 게시판 생성
3. 생성된 게시판 ID를 확인하여 `.env` 파일에 설정

### 5. 테스트

1. mg_wrap 프론트엔드: `http://localhost:8400`
2. Google 계정으로 로그인
3. 동일한 Google 계정으로 ig-board에도 로그인 (한 번만)
4. mg_wrap에서 "문의하기" 게시판에 게시글 작성 시도

## 문제 해결

### 에러: "Authentication required"
- mg_wrap 사용자가 ig-board에 등록되지 않았습니다.
- 해결: ig-board에 동일한 Google 계정으로 로그인하여 등록하세요.

### 에러: "Invalid token"
- `IG_BOARD_SECRET_KEY`가 잘못 설정되었습니다.
- 해결: ig-board의 `SECRET_KEY`와 동일한 값으로 설정하세요.

### 에러: "Board not found"
- `INQUIRY_BOARD_ID`가 잘못 설정되었습니다.
- 해결: ig-board에서 게시판 ID를 확인하고 올바르게 설정하세요.

### 에러: "Connection error"
- ig-board 서버가 실행되지 않았습니다.
- 해결: ig-board 백엔드를 실행하세요:
  ```bash
  cd /Users/ignite/Documents/AI\ Coding/cursor_project/ig-board/backend
  uvicorn app.main:app --reload --port 8301
  ```

## 현재 상태

- ✅ 게시글 목록 조회: 작동 (인증 불필요)
- ✅ 게시글 상세 조회: 작동 (인증 불필요)
- ⚠️ 게시글 작성: ig-board에 사용자 등록 필요
- ⚠️ 댓글 작성: ig-board에 사용자 등록 필요

## 향후 개선 사항

1. 자동 사용자 동기화: mg_wrap 사용자가 로그인할 때 자동으로 ig-board에도 사용자 생성
2. 통합 인증 시스템: mg_wrap과 ig-board가 같은 인증 시스템 사용
3. 관리자 API: ig-board에 관리자 API를 통해 사용자 생성 가능하도록 확장

