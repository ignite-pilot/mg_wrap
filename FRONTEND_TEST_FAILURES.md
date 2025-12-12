# Frontend 테스트 실패 케이스 상세 분석

## 전체 요약
- **총 테스트**: 17개
- **통과**: 12개 (71%)
- **실패**: 5개 (29%)

---

## 실패 케이스 1: Home.test.jsx - "renders 4 feature cards (2.1)"

### 에러 메시지
```
TestingLibraryElementError: Found multiple elements with the text: 공간형 자산보관

Here are the matching elements:
<h3>공간형 자산보관</h3>  (features 섹션)
<h3>공간형 자산보관</h3>  (pricing 섹션)

(If this is intentional, then use the `*AllBy*` variant of the query 
(like `queryAllByText`, `getAllByText`, or `findAllByText`)).
```

### 원인 분석
1. **문제 위치**: `Home.jsx`에서 "공간형 자산보관" 텍스트가 두 곳에 존재
   - **Features 섹션** (라인 44): `<h3>공간형 자산보관</h3>` - 기능 소개 카드
   - **Pricing 섹션** (라인 95): `<h3>공간형 자산보관</h3>` - 요금 정책 카드

2. **테스트 코드 문제**: 
   - `screen.getByText('공간형 자산보관')` 사용
   - `getByText`는 단일 요소만 반환 가능
   - 동일한 텍스트가 2개 이상 존재하면 에러 발생

3. **실제 HTML 구조**:
   ```html
   <!-- Features 섹션 -->
   <div class="features-section">
     <div class="feature-card">
       <h3>공간형 자산보관</h3>  <!-- 첫 번째 -->
     </div>
   </div>
   
   <!-- Pricing 섹션 -->
   <div class="pricing-section">
     <div class="pricing-card">
       <h3>공간형 자산보관</h3>  <!-- 두 번째 -->
     </div>
   </div>
   ```

### 해결 방법
1. **옵션 1**: 테스트 코드 수정 (권장)
   - `getAllByText` 사용하여 모든 요소 찾기
   - 또는 특정 섹션 내에서만 검색 (`within` 사용)

2. **옵션 2**: 컴포넌트 수정
   - Pricing 섹션의 텍스트를 다르게 변경 (예: "공간형 자산보관 요금")

### 권장 수정 코드
```javascript
it('renders 4 feature cards (2.1)', () => {
  render(
    <BrowserRouter>
      <Home />
    </BrowserRouter>
  )
  // getAllByText 사용하여 모든 요소 찾기
  const spaceStorageTexts = screen.getAllByText('공간형 자산보관')
  expect(spaceStorageTexts.length).toBeGreaterThanOrEqual(1)
  
  // 또는 within을 사용하여 특정 섹션만 검색
  const featuresSection = screen.getByText('필요한 평수에 맞춰 유연하게 보관 공간을 제공합니다.').closest('.features-section')
  expect(within(featuresSection).getByText('공간형 자산보관')).toBeInTheDocument()
  
  expect(screen.getByText('BOX형 자산보관')).toBeInTheDocument()
  expect(screen.getByText('실시간 자산 관리')).toBeInTheDocument()
  expect(screen.getByText('회수 및 폐기 신청')).toBeInTheDocument()
})
```

---

## 실패 케이스 2-5: StorageApplication.test.jsx - Label-Input 연결 문제

### 공통 에러 메시지
```
TestingLibraryElementError: Found a label with the text of: /평수/, 
however no form control was found associated to that label. 
Make sure you're using the "for" attribute or "aria-labelledby" 
attribute correctly.
```

### 실패한 테스트 목록
1. `shows space input when space type is selected (3.1)` - 라인 47
2. `shows box input when box type is selected (3.2)` - 라인 58
3. `calls API for estimate (3.1)` - 라인 88
4. `shows error message on API failure (11.1)` - 라인 118

### 원인 분석

#### 1. HTML 구조 문제
현재 `StorageApplication.jsx`의 label-input 구조:
```jsx
<div className="form-group">
  <label>평수</label>  {/* htmlFor 속성 없음 */}
  <input
    type="number"
    min="1"
    placeholder="평수를 입력하세요"
    value={spacePyeong}
    onChange={(e) => setSpacePyeong(e.target.value)}
  />
</div>
```

#### 2. 문제점
- `<label>`에 `htmlFor` 속성이 없음
- `<input>`에 `id` 속성이 없음
- React Testing Library의 `getByLabelText`는 label과 input이 명시적으로 연결되어 있어야 작동
- 연결 방법:
  - `label.htmlFor === input.id` 또는
  - `input`이 `label` 내부에 중첩되어 있거나
  - `aria-labelledby` 속성 사용

#### 3. 현재 상태
- Label과 Input이 형제 요소로 존재
- 시각적으로는 연결되어 보이지만, 접근성(accessibility) 관점에서 연결되지 않음
- 스크린 리더 사용자나 테스트 도구가 label-input 관계를 인식하지 못함

### 해결 방법

#### 옵션 1: htmlFor와 id 추가 (권장)
```jsx
<div className="form-group">
  <label htmlFor="space-pyeong">평수</label>
  <input
    id="space-pyeong"
    type="number"
    min="1"
    placeholder="평수를 입력하세요"
    value={spacePyeong}
    onChange={(e) => setSpacePyeong(e.target.value)}
  />
</div>

<div className="form-group">
  <label htmlFor="box-count">BOX 수량</label>
  <input
    id="box-count"
    type="number"
    min="1"
    placeholder="BOX 수량을 입력하세요"
    value={boxCount}
    onChange={(e) => setBoxCount(e.target.value)}
  />
</div>
```

#### 옵션 2: Input을 Label 내부에 중첩
```jsx
<label>
  평수
  <input
    type="number"
    min="1"
    placeholder="평수를 입력하세요"
    value={spacePyeong}
    onChange={(e) => setSpacePyeong(e.target.value)}
  />
</label>
```

#### 옵션 3: 테스트 코드 수정 (임시 해결책)
```javascript
// getByLabelText 대신 getByPlaceholderText 사용
const spaceInput = screen.getByPlaceholderText('평수를 입력하세요')
```

### 권장 수정 사항

**StorageApplication.jsx 수정**:
```jsx
// 평수 입력 필드
<div className="form-group">
  <label htmlFor="space-pyeong">평수</label>
  <input
    id="space-pyeong"
    type="number"
    min="1"
    placeholder="평수를 입력하세요"
    value={spacePyeong}
    onChange={(e) => setSpacePyeong(e.target.value)}
  />
</div>

// BOX 수량 입력 필드
<div className="form-group">
  <label htmlFor="box-count">BOX 수량</label>
  <input
    id="box-count"
    type="number"
    min="1"
    placeholder="BOX 수량을 입력하세요"
    value={boxCount}
    onChange={(e) => setBoxCount(e.target.value)}
  />
</div>

// 보관 개월수 선택 필드
<div className="form-group">
  <label htmlFor="months">보관 개월수</label>
  <select
    id="months"
    value={months}
    onChange={(e) => setMonths(parseInt(e.target.value))}
  >
    <option value="1">1개월</option>
    <option value="3">3개월</option>
    <option value="6">6개월</option>
  </select>
</div>
```

---

## 테스트 실패 영향도 분석

### 심각도: 낮음
- 모든 실패는 **테스트 코드 또는 접근성(accessibility) 문제**
- 실제 기능 동작에는 문제 없음
- 사용자 경험에는 영향 없음

### 우선순위
1. **높음**: StorageApplication label-input 연결 수정
   - 접근성 개선 (스크린 리더 지원)
   - 테스트 통과

2. **중간**: Home 테스트 코드 수정
   - 테스트만 수정하면 해결 가능
   - 기능 변경 불필요

---

## 수정 후 예상 결과
- **통과 예상**: 17개 모두 통과 (100%)
- **접근성 개선**: 스크린 리더 사용자 지원 향상
- **코드 품질**: 더 나은 테스트 커버리지

