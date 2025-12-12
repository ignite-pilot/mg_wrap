# AWS 배포 설정

이 디렉토리는 MG-Wrap Enterprise 애플리케이션을 AWS에 배포하기 위한 파일들을 포함합니다.

## 디렉토리 구조

```
.aws/
├── cloudformation/
│   └── all-in-one.yaml          # CloudFormation 템플릿
├── scripts/
│   ├── deploy.sh                # 배포 스크립트
│   └── destroy.sh               # 스택 삭제 스크립트
├── DEPLOYMENT.md                # 상세 배포 가이드
└── README.md                    # 이 파일
```

## 빠른 시작

### 1. 배포

```bash
# 기본 배포 (데이터베이스 비밀번호만)
./.aws/scripts/deploy.sh <YOUR_AWS_PROFILE> alpha 'YourDBPassword123!'

# Google OAuth 포함
./.aws/scripts/deploy.sh <YOUR_AWS_PROFILE> alpha 'YourDBPassword123!' \
  'google-client-id' 'google-client-secret'
```

### 2. 애플리케이션 URL 확인

```bash
aws cloudformation describe-stacks \
  --profile <YOUR_AWS_PROFILE> \
  --region ap-northeast-2 \
  --stack-name alpha-mg-wrap-enterprise-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
  --output text
```

### 3. 로그 확인

```bash
aws logs tail /ecs/alpha-mg-wrap-enterprise --follow \
  --profile <YOUR_AWS_PROFILE> --region ap-northeast-2
```

### 4. 스택 삭제

```bash
./.aws/scripts/destroy.sh <YOUR_AWS_PROFILE> alpha
```

## 환경 구분

- **alpha**: 개발/테스트 환경
  - FARGATE_SPOT 사용 (비용 절감)
  - db.t3.micro (최소 RDS 인스턴스)
  - 단일 가용 영역

- **prod**: 프로덕션 환경
  - FARGATE 사용 (안정성)
  - db.t3.small, Multi-AZ (고가용성)
  - 2개 이상의 태스크

## 주요 리소스

배포 시 생성되는 AWS 리소스:

1. **네트워킹**
   - Application Load Balancer (인터넷 연결)
   - Security Groups (ALB, ECS, RDS)

2. **컴퓨팅**
   - ECR Repository (Docker 이미지 저장소)
   - ECS Cluster (Fargate)
   - ECS Service & Tasks

3. **데이터베이스**
   - RDS PostgreSQL 인스턴스
   - RDS Subnet Group

4. **모니터링**
   - CloudWatch Log Group

5. **보안 & 인증** (선택사항)
   - ACM Certificate (HTTPS)
   - Route53 Record (도메인)

## 비용 예상

### Alpha 환경 (월 예상)
- ECS Fargate Spot: ~$10-20
- RDS db.t3.micro: ~$15
- ALB: ~$16
- **총 예상: ~$45-55/월**

### Production 환경 (월 예상)
- ECS Fargate: ~$30-50
- RDS db.t3.small (Multi-AZ): ~$60
- ALB: ~$16
- **총 예상: ~$110-130/월**

*실제 비용은 트래픽량과 사용 패턴에 따라 달라질 수 있습니다.*

## 자세한 정보

전체 배포 가이드는 [DEPLOYMENT.md](./DEPLOYMENT.md)를 참조하세요.

## 문제 해결

### 배포 실패 시

1. CloudFormation 이벤트 확인:
   ```bash
   aws cloudformation describe-stack-events \
     --stack-name alpha-mg-wrap-enterprise-stack \
     --profile <YOUR_AWS_PROFILE> \
     --max-items 20
   ```

2. ECS 서비스 이벤트 확인:
   ```bash
   aws ecs describe-services \
     --cluster alpha-mg-wrap-enterprise-cluster \
     --services alpha-mg-wrap-enterprise-service \
     --profile <YOUR_AWS_PROFILE>
   ```

3. 로그 확인:
   ```bash
   aws logs tail /ecs/alpha-mg-wrap-enterprise \
     --follow --profile <YOUR_AWS_PROFILE>
   ```
