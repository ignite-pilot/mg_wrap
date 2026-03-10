

# 맡길랩 엔터프라이즈 웹 서비스 설명

	- 맡길랩 엔터프라이즈는 짐 보관을 해 주는 맡길랩 서비스의 B2B 전용 사이트입니다.
	- 디자인 컨셉은 맡길랩 홈페이지 https://mg-wrap.com/ 와 동일한 느낌으로 만들어 주세요.
	- 맡길랩이 개인 대상 짐 보관이라고 한다면, 맡길랩 엔터프라이지는 기업을 위한 짐 보관 서비스 입니다.
	- 웹 서비스는 같은 기능을 제공합니다.
		- 메인 페이지
			- 맡길랩 엔터프라이즈에 대한 소개 및 기능 링크
		- 회원
			- ig-member 서비스를 통한 회원 관리 (구글 회원가입, 로그인, 로그아웃)
			- 자체 회원 관리 기능은 제거되고 ig-member MCP로 대체됨
		- 보관 신청
			- 고객은 "공간형 자산보관"과 "BOX형 자산보관"을 신청할 수 있습니다.
			- 공간형 자산보관은 필요한 평수와 보관 개월수를 입력하면 견적금액이 노출됩니다.
			- BOX형 자산보관은 BOX 수량과 보관 개월수를 입력하면 견적금액이 노출됩니다.
			- 견적 금액 노출 후, 최종 신청 버튼을 누르면 보관 "보관 자산","회수 현황","페기 현황" 메뉴 사용이 가능합니다.
		- 가격 정책
			- "공간형 자산보관"
				- 5평기준
					- 1개월 - 300,000원
					- 3개월 - 800,000원
					- 6개월 - 1,500,000원
			- "BOX형 자산보관"
				- BOX 1개 (60L) 기준
					- 1개월 - 30,000원
					- 3개월 - 80,000원
					- 6개월 - 150,000원
		- 보관 자산 현황
			- 보관 자산을 개별 입력하거나, 엑셀 업로드로 입력할 수 있습니다.
			- 자산 현황은 아래의 필드를 가집니다.
				- 자산번호 - 시스템에서 자동 부여한 번호
				- 보관 신청일 
				- 보관 시작일
				- 자산 분류
					- 사무용품, 서류, 장비, 가구, 의류, 가전, 기타로 나누어집니다.
				- 특이사항
			- 등록된 자산은 리스트 형태로 볼 수 있습니다.
			- 각각의 항목은 회수 신청, 페기 신청 버튼을 통해서 신청을 할 수 있습니다.
		- 회수 현황
			- 회수 신청한 목록이 노출됩니다.
			- 회수 상태는 "출고 준비중","출고중","회수 완료"로 나눠서 표시됩니다.
			- "출고 준비중"인 경우는 "회수 취소" 버튼을 통해서 취소가 가능합니다.
		- 페기 현황
			- 페기 신청한 목록이 노출됩니다.
			- 페기 상태는 "페기 준비중","페기 완료"로 표시됩니다.
			- "페기 준비중"인 경우는 "페기 취소"버튼을 통해서 페기 취소가 가능합니다.



# 개발 Guide


- Github : https://github.com/marojun/mg-wrap-enterprise.git
- Database는 aidev-pgvector-dev.crkgaskg6o61.ap-northeast-2.rds.amazonaws.com
Port : 5432
User    :  postgres
Password:  vmcMrs75!KZHk2johkRR:]wL
DB 명 : mg-wrap
- 개발 언어는 서버쪽은 Python을 활용하고, Front End는 괜찮은 걸로 알아서 진행

- Server Port
	- 단일 서비스: 8400 (Frontend + Backend 통합)
	- 접속 URL
		- 서비스: http://localhost:8400
		- API 엔드포인트: http://localhost:8400/api/*
	- ig-board MCP Port
		- ig-board Frontend: 8300
		- ig-board Backend: 8301
		- ig-board MCP Server: 8302
		- ig-board API URL: http://localhost:8301
	- ig-member MCP Port
		- ig-member Frontend: 8200
		- ig-member Backend: 8201
		- ig-member MCP Server: 8202
		- ig-member API URL: http://localhost:8201/api
		- 회원 관리: ig-member 서비스를 통해 처리 (자체 회원 관리 기능 제거)
	