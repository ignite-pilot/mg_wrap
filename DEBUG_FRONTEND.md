# 프론트엔드 디버깅 가이드

## 문제: http://localhost:3000/ 화면이 뜨지 않음

### 1. 개발 서버 확인 및 재시작

터미널에서 다음 명령어를 실행하세요:

```bash
cd frontend
npm run dev
```

서버가 정상적으로 시작되면 다음과 같은 메시지가 표시됩니다:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### 2. 브라우저 콘솔 확인

브라우저에서 `F12` 또는 `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)를 눌러 개발자 도구를 열고 Console 탭을 확인하세요.

오류 메시지가 있으면 알려주세요.

### 3. 포트 확인

포트 3000이 이미 사용 중인 경우:

```bash
# 포트 3000을 사용하는 프로세스 확인
lsof -ti:3000

# 프로세스 종료
kill -9 $(lsof -ti:3000)

# 다시 시작
cd frontend
npm run dev
```

### 4. 필요한 서버 실행 확인

다음 서버들이 실행 중이어야 합니다:

1. **백엔드 서버 (포트 5000)**
   ```bash
   cd /Users/ignite/Documents/AI\ Coding/cursor_project/mg_wrap
   python run.py
   ```

2. **ig-board 서버 (포트 8301)** - 게시판 기능 사용 시
   ```bash
   cd /Users/ignite/Documents/AI\ Coding/cursor_project/ig-board/backend
   uvicorn app.main:app --reload --port 8301
   ```

### 5. 환경 변수 확인

프론트엔드에서 게시판을 사용하려면 백엔드의 `.env` 파일에 다음이 설정되어 있어야 합니다:

```env
IG_BOARD_API_URL=http://localhost:8301
INQUIRY_BOARD_ID=2
```

### 6. 브라우저 캐시 삭제

브라우저 캐시 문제일 수 있습니다:
- `Cmd+Shift+R` (Mac) / `Ctrl+Shift+R` (Windows)로 강력 새로고침
- 또는 브라우저 캐시를 완전히 삭제

### 7. 종속성 재설치

문제가 계속되면:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### 8. 일반적인 오류

#### "Cannot GET /"
- 프론트엔드 개발 서버가 실행되지 않았습니다
- `npm run dev` 실행

#### "Network Error" 또는 CORS 오류
- 백엔드 서버가 실행되지 않았습니다
- `python run.py` 실행

#### 게시판 관련 오류
- ig-board 서버가 실행되지 않았거나
- 환경 변수가 설정되지 않았습니다

