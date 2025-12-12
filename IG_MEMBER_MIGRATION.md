# ig-member 서비스로 전환 가이드

## 개요

mg_wrap의 회원 관리 기능을 제거하고 ig-member 서비스를 사용하도록 전환했습니다.

## 변경 사항

### 1. 회원 관리 기능 제거
- ✅ `User` 모델 제거
- ✅ 자체 Google OAuth 인증 제거
- ✅ JWT 토큰 생성 로직 제거 (ig-member에서 발급한 토큰 사용)

### 2. ig-member 통합
- ✅ `app/services/member_service.py` 생성 - ig-member API 클라이언트
- ✅ `app/routes/auth.py` 수정 - ig-member API 사용
- ✅ `get_current_user()` 함수 수정 - ig-member API를 통해 사용자 정보 조회

### 3. 데이터베이스 변경
- ✅ `users` 테이블 외래키 제약조건 제거
- ✅ `storage_applications.user_id`는 이제 ig-member의 사용자 ID를 저장 (외래키 없음)

### 4. 테스트 수정
- ✅ 모든 테스트에서 `MemberService.verify_token` 모킹
- ✅ User 모델 참조 제거

## 환경 변수 설정

`.env` 파일에 다음 환경 변수를 추가하세요:

```env
# ig-member API 설정
IG_MEMBER_API_URL=http://localhost:8201/api
IG_MEMBER_FRONTEND_URL=http://localhost:8200
```

## API 변경 사항

### 인증 엔드포인트

#### `/api/auth/google` (Deprecated)
- **상태**: 더 이상 사용되지 않음
- **대체**: 프론트엔드에서 ig-member의 OAuth2 플로우 사용
- **응답**: 301 리다이렉트 안내

#### `/api/auth/verify`
- **변경**: ig-member API를 통해 토큰 검증
- **요청**: `Authorization: Bearer {token}` 헤더 필요
- **응답**: ig-member에서 반환한 사용자 정보

### 사용자 정보 형식

이제 `get_current_user()`는 딕셔너리를 반환합니다:

```python
{
    'id': 1,  # ig-member의 사용자 ID
    'email': 'user@example.com',
    'name': 'User Name'
}
```

**변경 전:**
```python
user = get_current_user()
user_id = user.id  # ❌ 작동하지 않음
```

**변경 후:**
```python
user = get_current_user()
user_id = user.get('id')  # ✅ 올바른 방법
```

## 프론트엔드 변경 필요

프론트엔드에서 Google 로그인을 처리할 때:

1. **기존 방식 (제거됨)**:
   ```javascript
   // 더 이상 작동하지 않음
   const response = await api.post('/api/auth/google', { token: googleToken });
   ```

2. **새로운 방식 (ig-member OAuth2 플로우)**:
   ```javascript
   // ig-member 로그인 페이지로 리다이렉트
   const returnUrl = encodeURIComponent('http://localhost:8400/auth/callback');
   window.location.href = `http://localhost:8200/login?returnUrl=${returnUrl}`;
   ```

3. **콜백 처리**:
   ```javascript
   // /auth/callback에서 일회용 코드로 토큰 받기
   const code = new URLSearchParams(window.location.search).get('code');
   const response = await fetch(`http://localhost:8201/api/auth/token/${code}`);
   const { token, user } = response.data.data;
   localStorage.setItem('token', token);
   ```

## 데이터베이스 마이그레이션

외래키 제약조건을 제거하려면:

```sql
ALTER TABLE storage_applications 
DROP CONSTRAINT IF EXISTS storage_applications_user_id_fkey;
```

이미 실행되었습니다 (`database/migration_remove_user_foreign_key.sql`).

## 테스트

모든 테스트는 `MemberService.verify_token`을 모킹하여 작동합니다:

```python
@patch('app.services.member_service.MemberService.verify_token')
def test_example(mock_verify, client):
    mock_verify.return_value = {
        'id': 1,
        'email': 'test@example.com',
        'name': 'Test User'
    }
    # 테스트 진행...
```

## 주의사항

1. **ig-member 서버 실행 필요**: mg_wrap을 사용하려면 ig-member 백엔드가 실행 중이어야 합니다.
2. **CORS 설정**: ig-member의 CORS 설정에 mg_wrap 프론트엔드 도메인을 추가해야 합니다.
3. **토큰 형식**: ig-member에서 발급한 JWT 토큰을 사용해야 합니다.

## 문제 해결

### "Member service error"
- ig-member 백엔드가 실행 중인지 확인
- `IG_MEMBER_API_URL` 환경 변수가 올바른지 확인

### "Invalid token"
- ig-member에서 발급한 토큰인지 확인
- 토큰이 만료되지 않았는지 확인

### "401 Unauthorized"
- `Authorization: Bearer {token}` 헤더가 올바르게 전달되는지 확인
- ig-member API가 정상 작동하는지 확인

