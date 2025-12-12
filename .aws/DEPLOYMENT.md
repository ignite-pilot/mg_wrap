# MG-Wrap Enterprise AWS 배포 가이드

이 문서는 MG-Wrap Enterprise 애플리케이션을 AWS에 배포하는 방법을 설명합니다.

## 목차

- [아키텍처 개요](#아키텍처-개요)
- [사전 준비사항](#사전-준비사항)
- [배포 방법](#배포-방법)
- [환경 변수 설정](#환경-변수-설정)
- [도메인 설정](#도메인-설정)
- [문제 해결](#문제-해결)
- [스택 삭제](#스택-삭제)

## 아키텍처 개요

배포된 인프라는 다음 AWS 서비스를 사용합니다:

- **ECS Fargate**: 컨테이너 실행 (서버리스)
- **Application Load Balancer (ALB)**: 트래픽 분산 및 HTTPS 종료
- **RDS PostgreSQL**: 관리형 데이터베이스
- **ECR**: Docker 이미지 저장소
- **CloudWatch Logs**: 애플리케이션 로그
- **ACM**: SSL/TLS 인증서 (HTTPS용)
- **Route53**: DNS 관리 (선택사항)
- **VPC**: 네트워크 격리

### 아키텍처 다이어그램

```
Internet
   |
   v
[Application Load Balancer] (HTTPS/HTTP)
   |
   v
[ECS Fargate Tasks] (Private Subnet)
   |
   +---> [RDS PostgreSQL] (Private Subnet)
```

## 사전 준비사항

### 1. AWS CLI 설치 및 설정

```bash
# AWS CLI 설치 확인
aws --version

# AWS 프로파일 설정 확인
aws configure --profile <YOUR_AWS_PROFILE>
```

### 2. Docker 설치

```bash
# Docker 설치 확인
docker --version
```

### 3. 필수 정보 준비

배포하기 전에 다음 정보를 준비하세요:

- **데이터베이스 비밀번호**: RDS PostgreSQL 마스터 비밀번호 (최소 8자)
- **Google OAuth 자격증명** (선택사항):
  - Google Client ID
  - Google Client Secret
- **Flask Secret Key** (선택사항): 세션 암호화를 위한 키

## 배포 방법

### 기본 배포 (최소 설정)

데이터베이스 비밀번호만으로 배포:

```bash
cd /Users/hwan/git/mg-wrap-enterprise

./.aws/scripts/deploy.sh <YOUR_AWS_PROFILE> alpha 'YourSecureDBPassword123!'
```

### Google OAuth 포함 배포

Google OAuth를 사용하려면:

```bash
./.aws/scripts/deploy.sh \
  <YOUR_AWS_PROFILE> \
  alpha \
  'YourSecureDBPassword123!' \
  'your-google-client-id.apps.googleusercontent.com' \
  'your-google-client-secret'
```

### 전체 설정 배포

모든 환경 변수를 포함한 배포:

```bash
./.aws/scripts/deploy.sh \
  <YOUR_AWS_PROFILE> \
  alpha \
  'YourSecureDBPassword123!' \
  'your-google-client-id.apps.googleusercontent.com' \
  'your-google-client-secret' \
  'your-flask-secret-key-change-this-in-production'
```

### 배포 스크립트 파라미터

```
./.aws/scripts/deploy.sh <AWS_PROFILE> <ENVIRONMENT> <DB_PASSWORD> [GOOGLE_CLIENT_ID] [GOOGLE_CLIENT_SECRET] [SECRET_KEY]
```

- **AWS_PROFILE**: AWS CLI 프로파일
- **ENVIRONMENT**: 환경 (alpha 또는 prod)
- **DB_PASSWORD**: RDS 마스터 비밀번호 (필수)
- **GOOGLE_CLIENT_ID**: Google OAuth 클라이언트 ID (선택)
- **GOOGLE_CLIENT_SECRET**: Google OAuth 클라이언트 시크릿 (선택)
- **SECRET_KEY**: Flask SECRET_KEY (선택)

### 배포 프로세스

배포 스크립트는 다음 단계를 자동으로 수행합니다:

1. **Docker 이미지 빌드**: Frontend와 Backend를 단일 이미지로 빌드
2. **ECR 로그인**: AWS ECR에 인증
3. **이미지 푸시**: ECR에 Docker 이미지 업로드
4. **CloudFormation 배포**: 인프라 생성/업데이트
5. **ECS 서비스 업데이트**: 새 이미지로 컨테이너 재배포

배포는 약 10-15분 소요됩니다.

## 환경 변수 설정

애플리케이션은 다음 환경 변수를 사용합니다:

### 자동 설정 (CloudFormation)

- `ENV`: 환경 이름 (alpha/prod)
- `APPLICATION_NAME`: 애플리케이션 이름
- `DB_HOST`: RDS 엔드포인트 주소
- `DB_PORT`: RDS 포트 (5432)
- `DB_NAME`: 데이터베이스 이름 (mg_wrap)
- `DB_USER`: 데이터베이스 사용자 (mgwrap_admin)
- `DB_PASSWORD`: 데이터베이스 비밀번호

### 수동 설정 (배포 시 파라미터로 전달)

- `GOOGLE_CLIENT_ID`: Google OAuth 클라이언트 ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth 클라이언트 시크릿
- `SECRET_KEY`: Flask 세션 암호화 키

## 도메인 설정

### 1. Public Hosted Zone 생성

현재 alpha.mg-wrap.com은 Private Hosted Zone으로 설정되어 있어 인터넷에서 접근할 수 없습니다.

인터넷에서 접근 가능하게 하려면:

```bash
# Public Hosted Zone 생성
aws route53 create-hosted-zone \
  --name alpha.mg-wrap.com \
  --caller-reference $(date +%s) \
  --profile <YOUR_AWS_PROFILE>
```

### 2. 도메인 설정으로 재배포

Hosted Zone ID를 확인한 후:

```bash
# Hosted Zone ID 조회
aws route53 list-hosted-zones \
  --profile <YOUR_AWS_PROFILE> \
  --query "HostedZones[?Name=='alpha.mg-wrap.com.'].Id" \
  --output text

# CloudFormation 파라미터에 추가
# .aws/cloudformation/all-in-one.yaml 파일을 사용하여
# DomainName과 HostedZoneId 파라미터를 설정하여 재배포
```

### 3. DNS 네임서버 설정

Public Hosted Zone을 만든 후, 도메인 등록 대행사에서 네임서버를 Route53 네임서버로 변경해야 합니다.

## 배포 확인

### 1. 스택 상태 확인

```bash
aws cloudformation describe-stacks \
  --profile <YOUR_AWS_PROFILE> \
  --region ap-northeast-2 \
  --stack-name alpha-mg-wrap-enterprise-stack \
  --query 'Stacks[0].StackStatus'
```

### 2. ECS 서비스 상태 확인

```bash
aws ecs describe-services \
  --profile <YOUR_AWS_PROFILE> \
  --region ap-northeast-2 \
  --cluster alpha-mg-wrap-enterprise-cluster \
  --services alpha-mg-wrap-enterprise-service
```

### 3. 로그 확인

```bash
# 실시간 로그 확인
aws logs tail \
  --profile <YOUR_AWS_PROFILE> \
  --region ap-northeast-2 \
  /ecs/alpha-mg-wrap-enterprise \
  --follow
```

### 4. 애플리케이션 URL 확인

```bash
aws cloudformation describe-stacks \
  --profile <YOUR_AWS_PROFILE> \
  --region ap-northeast-2 \
  --stack-name alpha-mg-wrap-enterprise-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
  --output text
```

## 문제 해결

### ECS 태스크가 시작되지 않음

1. **로그 확인**:
   ```bash
   aws logs tail /ecs/alpha-mg-wrap-enterprise --follow --profile <YOUR_AWS_PROFILE> --region ap-northeast-2
   ```

2. **태스크 상태 확인**:
   ```bash
   aws ecs list-tasks \
     --cluster alpha-mg-wrap-enterprise-cluster \
     --service-name alpha-mg-wrap-enterprise-service \
     --profile <YOUR_AWS_PROFILE> \
     --region ap-northeast-2
   ```

### 데이터베이스 연결 오류

1. **RDS 엔드포인트 확인**:
   ```bash
   aws cloudformation describe-stacks \
     --stack-name alpha-mg-wrap-enterprise-stack \
     --profile <YOUR_AWS_PROFILE> \
     --region ap-northeast-2 \
     --query 'Stacks[0].Outputs[?OutputKey==`RDSEndpoint`].OutputValue'
   ```

2. **보안 그룹 규칙 확인**: ECS Security Group이 RDS Security Group에 접근할 수 있는지 확인

### ALB 헬스체크 실패

1. **/api/health 엔드포인트 확인**: 애플리케이션이 정상적으로 응답하는지 확인
2. **보안 그룹 확인**: ALB에서 ECS 태스크로 트래픽이 허용되는지 확인

## 데이터베이스 스키마 적용

처음 배포 후 데이터베이스 스키마를 적용해야 합니다:

### 방법 1: ECS 태스크에서 직접 실행

```bash
# ECS 태스크 ID 확인
TASK_ARN=$(aws ecs list-tasks \
  --cluster alpha-mg-wrap-enterprise-cluster \
  --service-name alpha-mg-wrap-enterprise-service \
  --profile <YOUR_AWS_PROFILE> \
  --region ap-northeast-2 \
  --query 'taskArns[0]' \
  --output text)

# ECS Exec으로 접속
aws ecs execute-command \
  --cluster alpha-mg-wrap-enterprise-cluster \
  --task ${TASK_ARN} \
  --container alpha-mg-wrap-enterprise-container \
  --command "/bin/sh" \
  --interactive \
  --profile <YOUR_AWS_PROFILE> \
  --region ap-northeast-2

# 컨테이너 안에서 스키마 적용
python apply_schema_properly.py
```

### 방법 2: 로컬에서 직접 연결

```bash
# RDS 엔드포인트 확인
RDS_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name alpha-mg-wrap-enterprise-stack \
  --profile <YOUR_AWS_PROFILE> \
  --region ap-northeast-2 \
  --query 'Stacks[0].Outputs[?OutputKey==`RDSEndpoint`].OutputValue' \
  --output text)

# psql로 접속 (VPN 또는 bastion 호스트 필요)
psql -h $RDS_ENDPOINT -U mgwrap_admin -d mg_wrap

# SQL 파일 실행
\i database/schema.sql
```

## 스택 삭제

⚠️ **경고**: 이 명령은 모든 리소스를 삭제합니다. RDS는 최종 스냅샷을 생성합니다.

```bash
./.aws/scripts/destroy.sh <YOUR_AWS_PROFILE> alpha
```

삭제되는 리소스:
- ECS Cluster, Service, Tasks
- Application Load Balancer
- RDS Database (스냅샷 생성 후)
- ECR Repository 및 모든 이미지
- Security Groups
- CloudWatch Log Groups
- IAM Roles

삭제는 약 15-20분 소요됩니다.

## 비용 최적화

### Alpha 환경 (개발/테스트)

- **ECS**: FARGATE_SPOT 사용 (최대 70% 저렴)
- **RDS**: db.t3.micro (약 $15/월)
- **ALB**: 시간당 과금 (약 $16/월)

### Production 환경

- **ECS**: FARGATE (안정성)
- **RDS**: db.t3.small, Multi-AZ (고가용성)
- **ALB**: 동일

### 비용 절감 팁

1. **사용하지 않을 때 중지**: Alpha 환경은 업무 시간 외 중지
   ```bash
   # ECS 서비스 중지
   aws ecs update-service \
     --cluster alpha-mg-wrap-enterprise-cluster \
     --service alpha-mg-wrap-enterprise-service \
     --desired-count 0 \
     --profile <YOUR_AWS_PROFILE>

   # 재시작
   aws ecs update-service \
     --cluster alpha-mg-wrap-enterprise-cluster \
     --service alpha-mg-wrap-enterprise-service \
     --desired-count 1 \
     --profile <YOUR_AWS_PROFILE>
   ```

2. **RDS 중지**: 개발 중 사용하지 않을 때 (최대 7일)
   ```bash
   aws rds stop-db-instance \
     --db-instance-identifier alpha-mg-wrap-enterprise-db \
     --profile <YOUR_AWS_PROFILE>
   ```

## 추가 리소스

- [AWS ECS 문서](https://docs.aws.amazon.com/ecs/)
- [AWS RDS 문서](https://docs.aws.amazon.com/rds/)
- [CloudFormation 템플릿 참조](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/)

## 지원

문제가 발생하면 다음을 확인하세요:

1. CloudWatch Logs: `/ecs/alpha-mg-wrap-enterprise`
2. CloudFormation Events: 스택 생성/업데이트 실패 이유
3. ECS Service Events: 태스크 시작 실패 이유
