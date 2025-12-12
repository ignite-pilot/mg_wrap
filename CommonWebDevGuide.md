- 초기 개발 작업은 Sequential Thinking을 사용해서 수행해줘
- 실제 코딩을 시작하기에 앞서, Git Repository 생성과 DB 생성부터 먼저해줘. 접속 정보는 아래 정보를 참고해줘
- frontend, backend를 하나의 서비스로 동작하도록 만들어줘
- 개발이 모두 완료 된 후에, 이 사이트의 모든 기능에 대해서 테스트 항목을 Sequential Thinking을 사용해서 만들어 주고, 실제 BE 및 FE unit test도 진행해주고, fail이 난 부분에 대해서는 바로 수정도 해줘.
- 모든 개발은 보안에 Safe하게 개발을 해줘
- 모든 개발은 정적분석코드에 위배되지 않도록 해줘
- 모든 코드 수정이 이뤄진 후에는 매번 unit test, 정적코드 분석, 보안 체크를 수행하고 수정이 필요하면 수정해줘
- Health Check를 위한 API를 "/api/health" 이런 Path로 반드시 만들어줘

# Git 정보
- Github에 Project 이름으로 Repository를 만들어줘. 
	- Github에 사용할 Personal Access Token은 AWS Secret Manager "prod/ignite-pilot/github"을 참고해서 사용해줘
# DB 정보
- Database는 AWS Secret Manager "prod/ignite-pilot/postgresInfo2"를 참고해서 만들어줘

- 실행 관련해서는 config.local.env 파일을 참고해서 만들어줘
- 실행할 서비스 도메인과 Port는 반드시 config.local.env에 지정한 값으로 해줘
- 작업이나 실행해 필요한 것들을 알아서 설치해줘
- 작업 완료 후, 배포를 위해서 dockerfile을 만들어줘