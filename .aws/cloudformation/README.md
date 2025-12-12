# MG-Wrap Enterprise CloudFormation Infrastructure

이 디렉토리에는 MG-Wrap Enterprise 애플리케이션의 AWS 인프라를 정의하는 CloudFormation 템플릿이 포함되어 있습니다.

## 파일 구조

```
.aws/cloudformation/
├── all-in-one.yaml              # 전체 인프라 정의 (템플릿)
├── parameters-alpha.json        # Alpha 환경 파라미터
└── README.md                    # 이 파일
```

## 포함된 리소스

이 템플릿은 다음 AWS 리소스를 생성합니다:

- **Networking**: Security Groups (ALB, ECS, RDS)
- **Database**: RDS PostgreSQL (암호화, 자동 백업)
- **Container Registry**: ECR Repository (라이프사이클 정책 포함)
- **Compute**: ECS Cluster, Task Definition, Service (Fargate)
- **Load Balancing**: Application Load Balancer, Target Group, HTTP/HTTPS Listeners
- **DNS & SSL**: Route53 Hosted Zone (선택), ACM SSL 인증서, DNS 레코드
- **Monitoring**: CloudWatch Logs

## 빠른 시작

### 1. 파라미터 파일 준비

`parameters-alpha.json` 파일을 복사하고 민감한 정보를 입력하세요:

```bash
cp parameters-alpha.json parameters-alpha.local.json
```

다음 값들을 실제 값으로 교체하세요:
- `DBPassword`: 데이터베이스 비밀번호 (최소 8자)
- `GoogleClientId`: Google OAuth Client ID (선택)
- `GoogleClientSecret`: Google OAuth Client Secret (선택)
- `SecretKey`: Flask 세션 암호화 키 (선택, 비워두면 자동 생성)

**중요**: `*.local.json` 파일은 `.gitignore`에 추가하여 커밋되지 않도록 하세요!

### 2. 스택 생성

```bash
aws cloudformation create-stack \
  --profile <YOUR_AWS_PROFILE> \
  --region ap-northeast-2 \
  --stack-name alpha-mg-wrap-enterprise-stack \
  --template-body file://all-in-one.yaml \
  --parameters file://parameters-alpha.local.json \
  --capabilities CAPABILITY_NAMED_IAM
```

### 3. 스택 업데이트

```bash
aws cloudformation update-stack \
  --profile <YOUR_AWS_PROFILE> \
  --region ap-northeast-2 \
  --stack-name alpha-mg-wrap-enterprise-stack \
  --template-body file://all-in-one.yaml \
  --parameters file://parameters-alpha.local.json \
  --capabilities CAPABILITY_NAMED_IAM
```

### 4. 스택 삭제

```bash
aws cloudformation delete-stack \
  --profile <YOUR_AWS_PROFILE> \
  --region ap-northeast-2 \
  --stack-name alpha-mg-wrap-enterprise-stack
```

## 파라미터 설명

### 필수 파라미터

| 파라미터 | 설명 | 기본값 |
|---------|------|-------|
| `Environment` | 환경 이름 (alpha, prod) | alpha |
| `ApplicationName` | 애플리케이션 이름 | mg-wrap-enterprise |
| `VpcId` | VPC ID | - |
| `PublicSubnetIds` | 퍼블릭 서브넷 IDs (ALB용) | - |
| `PrivateSubnetIds` | 프라이빗 서브넷 IDs (ECS, RDS용) | - |
| `DBUsername` | 데이터베이스 사용자 이름 | mgwrap_admin |
| `DBPassword` | 데이터베이스 비밀번호 | - |
| `DBName` | 데이터베이스 이름 | mg_wrap |

### 도메인 설정

| 파라미터 | 설명 | 기본값 |
|---------|------|-------|
| `RootDomain` | 루트 도메인 (예: ig-pilot.com) | ig-pilot.com |
| `CreateHostedZone` | Route53 Hosted Zone 생성 여부 | false |
| `HostedZoneId` | 기존 Hosted Zone ID (CreateHostedZone=false일 때) | - |

### 선택 파라미터

| 파라미터 | 설명 | 기본값 |
|---------|------|-------|
| `ContainerPort` | 컨테이너 포트 | 5000 |
| `HealthCheckPath` | 헬스 체크 경로 | /api/health |
| `GoogleClientId` | Google OAuth Client ID | "" |
| `GoogleClientSecret` | Google OAuth Client Secret | "" |
| `SecretKey` | Flask SECRET_KEY | "" (자동 생성) |

## 도메인 패턴

이 템플릿은 다음 도메인 패턴을 사용합니다:

- **Alpha 환경**: `alpha.mg-wrap-enterprise.ig-pilot.com`
- **Production 환경**: `mg-wrap-enterprise.ig-pilot.com`

와일드카드 SSL 인증서 (`*.mg-wrap-enterprise.ig-pilot.com`)가 자동으로 발급되어 모든 환경에서 사용됩니다.

## 도메인 설정 가이드

### 1. Route53에서 Hosted Zone 생성 (CreateHostedZone=true)

템플릿이 자동으로 Hosted Zone을 생성합니다. 생성 후:

1. 스택 출력에서 `HostedZoneNameServers` 확인
2. 도메인 등록업체에서 네임서버를 Route53 네임서버로 변경

### 2. 기존 Hosted Zone 사용 (CreateHostedZone=false)

이미 Hosted Zone이 있는 경우:

1. `HostedZoneId` 파라미터에 기존 Zone ID 입력
2. `CreateHostedZone`을 `false`로 설정

## 환경별 리소스 크기

템플릿은 환경에 따라 자동으로 리소스 크기를 조정합니다:

### Alpha 환경
- **RDS**: db.t3.micro, 20GB, 단일 AZ
- **ECS**: 1 vCPU, 2GB RAM, 1 task, FARGATE_SPOT
- **백업**: 3일 보관

### Production 환경
- **RDS**: db.t3.small, 50GB, Multi-AZ
- **ECS**: 2 vCPU, 4GB RAM, 2 tasks, FARGATE
- **백업**: 7일 보관

## 스택 출력

스택 생성 후 다음 정보를 확인할 수 있습니다:

```bash
aws cloudformation describe-stacks \
  --profile <YOUR_AWS_PROFILE> \
  --region ap-northeast-2 \
  --stack-name alpha-mg-wrap-enterprise-stack \
  --query 'Stacks[0].Outputs'
```

주요 출력:
- `ApplicationURL`: 애플리케이션 접속 URL
- `ApplicationDomain`: 도메인 이름
- `LoadBalancerDNS`: ALB DNS 이름
- `ECRRepositoryURI`: Docker 이미지 푸시 대상
- `RDSEndpoint`: 데이터베이스 엔드포인트
- `CertificateArn`: SSL 인증서 ARN

## 사전 요구사항

### 1. AWS 리소스
- VPC with public/private subnets
- IAM Role: `ecsTaskExecutionRole`

### 2. 도메인
- 도메인 등록 완료
- 도메인 관리 권한

### 3. Docker 이미지
- ECR에 푸시된 애플리케이션 이미지 (`latest` 태그)

## 배포 순서

전체 애플리케이션을 배포하려면:

1. **CloudFormation 스택 생성** (이 템플릿)
   ```bash
   aws cloudformation create-stack ...
   ```

2. **Docker 이미지 빌드 & 푸시**
   ```bash
   # ECR 로그인
   aws ecr get-login-password --profile <YOUR_AWS_PROFILE> --region ap-northeast-2 | \
     docker login --username AWS --password-stdin 615835782141.dkr.ecr.ap-northeast-2.amazonaws.com

   # 이미지 빌드 & 푸시
   docker build -t mg-wrap-enterprise .
   docker tag mg-wrap-enterprise:latest <ECR_URI>:latest
   docker push <ECR_URI>:latest
   ```

3. **ECS 서비스 업데이트** (새 이미지 배포)
   ```bash
   aws ecs update-service \
     --profile <YOUR_AWS_PROFILE> \
     --region ap-northeast-2 \
     --cluster alpha-mg-wrap-enterprise-cluster \
     --service alpha-mg-wrap-enterprise-service \
     --force-new-deployment
   ```

4. **도메인 네임서버 설정** (CreateHostedZone=true인 경우)
   - Route53에서 생성된 네임서버를 도메인 등록업체에 설정

## 문제 해결

### ACM 인증서 검증 실패

ACM 인증서가 `PENDING_VALIDATION` 상태에서 진행되지 않는 경우:

1. DNS가 올바르게 설정되었는지 확인:
   ```bash
   dig @8.8.8.8 _<validation-hash>.mg-wrap-enterprise.ig-pilot.com CNAME
   ```

2. 도메인 네임서버가 Route53으로 설정되었는지 확인:
   ```bash
   dig @8.8.8.8 ig-pilot.com NS
   ```

3. DNS 전파 대기 (최대 48시간, 보통 1-2시간)

### ECS 태스크 시작 실패

1. ECR에 이미지가 있는지 확인
2. CloudWatch Logs에서 오류 확인
3. Task Definition의 환경 변수 확인

### RDS 연결 실패

1. Security Group 규칙 확인
2. VPC 설정 확인 (private subnet에 RDS 배치)
3. 데이터베이스 엔드포인트 확인

## 보안 모범 사례

1. **비밀번호 관리**
   - 파라미터 파일에 직접 저장하지 말고 AWS Secrets Manager 사용 권장
   - 최소 16자 이상의 강력한 비밀번호 사용

2. **네트워크 격리**
   - RDS는 private subnet에만 배치
   - ECS tasks는 필요한 경우에만 public IP 할당

3. **암호화**
   - RDS 저장소 암호화 활성화 (기본 설정)
   - SSL/TLS 인증서 사용 (ACM)

4. **백업**
   - RDS 자동 백업 활성화
   - 중요 데이터는 추가 백업 고려

## 비용 최적화

- **Alpha 환경**: FARGATE_SPOT 사용으로 최대 70% 비용 절감
- **Production 환경**: 안정성을 위해 FARGATE 사용
- **RDS**: 개발 환경은 단일 AZ, 프로덕션은 Multi-AZ

## 라이선스

이 템플릿은 MG-Wrap Enterprise 프로젝트의 일부입니다.
