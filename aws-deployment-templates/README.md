# AWS 애플리케이션 배포 템플릿

최소한의 설정으로 AWS에 애플리케이션을 자동 배포하는 CloudFormation 템플릿 및 스크립트입니다.

## 🎯 주요 기능

- ✅ **Static & Full-Stack 앱 모두 지원**
  - Static: React, Vue, Angular 등 SPA → S3 + CloudFront
  - Full-Stack: Node.js, Python 등 백엔드 앱 → ECS + RDS + ALB

- ✅ **최소 4줄 설정으로 배포**
  ```yaml
  application_name: "my-app"  # 언더스코어(_)는 자동으로 하이픈(-)으로 변환
  deployment_phase: "alpha"
  aws_profile: "default"
  root_domain: "ig-pilot.com"
  ```

- ✅ **Fail-Fast 전략으로 빠른 실패 감지**
  - 키보드 입력 없음 (모든 값은 config 파일 또는 환경 변수)
  - 필수 값 누락 시 즉시 종료 및 명확한 에러 메시지
  - set -euo pipefail로 모든 에러 즉시 감지

- ✅ **자동 감지 기능** (80% 이상 자동화)
  - App Type (Dockerfile 또는 dist/build 폴더)
  - VPC & Subnets (태그 기반 검색)
  - Hosted Zone (도메인 기반 검색)
  - Container Port (Dockerfile EXPOSE)
  - AWS Region (Profile 설정)

- ✅ **환경별 자동 접근 제어**
  - Alpha/Beta: VPN 전용 (Security Group + WAF)
  - Production: 인터넷 공개

- ✅ **도메인 자동 설정**
  - Alpha: `alpha.{app}.ig-pilot.com`
  - Beta: `beta.{app}.ig-pilot.com`
  - Production: `{app}.ig-pilot.com`

- ✅ **리소스 자동 최적화**
  - Alpha/Beta: FARGATE_SPOT, db.t3.micro, 비용 절감
  - Production: FARGATE, db.t3.small (Multi-AZ), 고가용성

## 📁 디렉토리 구조

```
aws-deployment-templates/
├── cloudformation/
│   ├── static-app.yaml          # S3 + CloudFront 템플릿
│   └── fullstack-app.yaml       # ECS + RDS + ALB 템플릿
├── scripts/
│   ├── deploy.sh                # 배포 스크립트
│   └── destroy.sh               # 삭제 스크립트
├── config.yaml                  # 설정 파일 (모든 옵션 및 예제 포함)
├── README.md                    # 이 파일
└── QUICKSTART.md                # 5분 빠른 시작
```

## 🚀 빠른 시작

### 1단계: 설정 파일 생성

```bash
cp config.yaml config.alpha.yaml
```

### 2단계: 설정 파일 수정 (4줄만!)

```yaml
application_name: "my-app"      # 본인의 앱 이름
deployment_phase: "alpha"       # alpha, beta, production
aws_profile: "default"          # AWS CLI profile
root_domain: "ig-pilot.com"     # 도메인
```

### 3단계: 배포

**Static 웹사이트:**
```bash
# 빌드 후
npm run build

# 배포
./scripts/deploy.sh config.alpha.yaml
```

**Full-Stack 애플리케이션:**
```bash
# DB 비밀번호 설정 (환경 변수 권장)
export DB_PASSWORD='your-secure-password'

# Dockerfile 있는 디렉토리에서 배포
./scripts/deploy.sh config.alpha.yaml
```

### 4단계: 접속

자동으로 표시되는 URL로 접속:
- `https://alpha.my-app.ig-pilot.com`

## 🔍 자동 감지 항목

| 항목 | 감지 방법 | 재정의 방법 |
|------|----------|------------|
| App Type | Dockerfile → fullstack<br>dist/build → static | `app_type: static` |
| AWS Region | AWS Profile 설정 | `aws_region: us-east-1` |
| VPC | 'dev' 또는 'ignite' 이름 우선 | `vpc.vpc_id: vpc-xxx` |
| Subnets | 태그에 'public'/'pub' 또는 'private'/'pri' | `vpc.public_subnet_ids: [...]` |
| VPN CIDR | Client VPN Endpoint | `vpc.vpn_cidr: 10.255.0.0/16` |
| Hosted Zone | 도메인명으로 검색 | `domain.hosted_zone_id: Z0xx` |
| Container Port | Dockerfile EXPOSE | `container_port: 8080` |

## 📝 설정 파일 예시

### 최소 설정 (권장)
```yaml
application_name: "my-app"
deployment_phase: "alpha"
aws_profile: "default"
root_domain: "ig-pilot.com"
```

### 수동 재정의
```yaml
application_name: "my-app"
deployment_phase: "alpha"
aws_profile: "default"
root_domain: "ig-pilot.com"

# 자동 감지 재정의
app_type: "fullstack"
aws_region: "us-east-1"

vpc:
  vpc_id: "vpc-custom-123"
  public_subnet_ids:
    - "subnet-111"
    - "subnet-222"

container_port: 3000
```

더 많은 옵션은 `config.yaml` 파일의 주석 참고

## 🗑️ 삭제

```bash
./scripts/destroy.sh config.alpha.yaml
```

## 📚 환경별 설정

### Alpha (개발/테스트)
- VPN 전용 접근
- FARGATE_SPOT (비용 절감)
- db.t3.micro, 20GB, 단일 AZ
- 1 task, 1 vCPU, 2GB RAM
- 백업 3일 보관
- **비용: ~$45-55/월**

### Beta (스테이징)
- VPN 전용 접근
- FARGATE_SPOT
- db.t3.micro, 20GB, 단일 AZ
- 1 task, 1 vCPU, 2GB RAM
- 백업 3일 보관
- **비용: ~$45-55/월**

### Production (운영)
- 인터넷 공개 접근
- FARGATE (안정성)
- db.t3.small, 50GB, Multi-AZ
- 2+ tasks, 2 vCPU, 4GB RAM
- 백업 7일 보관
- **비용: ~$110-130/월**

## 🎨 사용 예시

### React SPA 배포
```bash
# 1. 빌드
npm run build

# 2. 설정 (4줄)
echo 'application_name: "my-react-app"
deployment_phase: "alpha"
aws_profile: "default"
root_domain: "ig-pilot.com"' > config.alpha.yaml

# 3. 배포
./scripts/deploy.sh config.alpha.yaml

# 자동 감지:
# ✅ App Type: static (build/ 폴더 발견)
# ✅ Region: ap-northeast-2
# ✅ Hosted Zone: Z029xxx
# ✅ VPN CIDR: 10.255.0.0/16
```

### Node.js API + PostgreSQL 배포
```bash
# 1. 설정 (4줄)
echo 'application_name: "my-api"
deployment_phase: "production"
aws_profile: "production"
root_domain: "ig-pilot.com"' > config.prod.yaml

# 2. 배포
./scripts/deploy.sh config.prod.yaml
# DB 비밀번호 입력: ********

# 자동 감지:
# ✅ App Type: fullstack (Dockerfile 발견)
# ✅ Container Port: 5000 (Dockerfile EXPOSE)
# ✅ VPC: vpc-xxx
# ✅ Subnets: subnet-xxx,yyy (public), subnet-aaa,bbb (private)
# ✅ Region: ap-northeast-2
```

## 🛠️ 고급 설정

### 데이터베이스 없는 Full-Stack 앱
```yaml
application_name: "ml-service"
deployment_phase: "alpha"
aws_profile: "default"
root_domain: "ig-pilot.com"

database:
  enabled: false

environment_variables:
  MODEL_PATH: "/app/models"
  REDIS_URL: "redis://external-redis:6379"
```

### MySQL 사용
```yaml
application_name: "my-app"
deployment_phase: "alpha"
aws_profile: "default"
root_domain: "ig-pilot.com"

database:
  engine: "mysql"
```

### 리소스 크기 커스터마이징
```yaml
application_name: "my-app"
deployment_phase: "alpha"
aws_profile: "default"
root_domain: "ig-pilot.com"

resources:
  rds_instance_class: "db.t3.medium"
  rds_allocated_storage: 100
  ecs_cpu: 2048
  ecs_memory: 4096
  ecs_desired_count: 3
```

## 🔧 운영 가이드

### 로그 확인 (Full-Stack)
```bash
aws logs tail /ecs/{phase}-{app-name} --follow --profile {profile}
```

### 스택 상태 확인
```bash
aws cloudformation describe-stacks \
  --stack-name {phase}-{app-name}-stack \
  --profile {profile}
```

### ECS 서비스 상태 (Full-Stack)
```bash
aws ecs describe-services \
  --cluster {phase}-{app-name}-cluster \
  --services {phase}-{app-name}-service \
  --profile {profile}
```

### CloudFront 캐시 무효화 (Static)
```bash
# Distribution ID 확인
aws cloudformation describe-stacks \
  --stack-name {phase}-{app-name}-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
  --output text

# 캐시 무효화
aws cloudfront create-invalidation \
  --distribution-id {distribution-id} \
  --paths "/*"
```

## ❓ 문제 해결

### "VPC를 찾을 수 없습니다"
→ VPC 태그에 'dev' 또는 'ignite' 추가, 또는:
```yaml
vpc:
  vpc_id: "vpc-xxx"
```

### "Public/Private Subnet을 찾을 수 없습니다"
→ Subnet 태그 이름에 'public'/'pub' 또는 'private'/'pri' 추가, 또는:
```yaml
vpc:
  public_subnet_ids: ["subnet-111", "subnet-222"]
  private_subnet_ids: ["subnet-333", "subnet-444"]
```

### "앱 타입 자동 감지 실패"
→ 수동으로 지정:
```yaml
app_type: "static"  # 또는 "fullstack"
```

### ACM 인증서 검증 대기 중
- DNS 전파 대기 (5-10분, 최대 48시간)
- Route53에 검증 레코드가 자동으로 추가됩니다

### ECS 태스크 시작 실패
```bash
# 로그 확인
aws logs tail /ecs/{phase}-{app-name} --follow

# 일반적인 원인:
# - Health check 실패 → health_check_path 확인
# - 리소스 부족 → ecs_cpu, ecs_memory 증가
```

## 📦 생성되는 리소스

### Static App
- S3 Bucket (정적 파일)
- CloudFront Distribution (CDN)
- Route53 DNS Record
- ACM Certificate (HTTPS)
- WAF Web ACL (Alpha/Beta만, VPN 제한)

### Full-Stack App
- ECR Repository (Docker 이미지)
- ECS Cluster, Service, Tasks (컨테이너)
- Application Load Balancer
- RDS Database (선택사항)
- Route53 DNS Record
- ACM Certificate (HTTPS)
- Security Groups (자동 설정)
- CloudWatch Logs

## 📖 추가 문서

- **[QUICKSTART.md](QUICKSTART.md)** - 5분 빠른 시작 가이드
- **[config.yaml](config.yaml)** - 전체 설정 옵션 및 예제 (주석 포함)

## 💡 모범 사례

1. **환경별 분리**
   ```bash
   config.alpha.yaml     # 개발
   config.beta.yaml      # 스테이징
   config.prod.yaml      # 운영
   ```

2. **민감 정보 관리**
   ```bash
   # Git에서 제외
   echo "config.*.yaml" >> .gitignore

   # 환경 변수 사용
   export DB_PASSWORD='SecurePassword123!'
   ```

3. **Production 배포 전 체크리스트**
   - [ ] Alpha/Beta에서 충분히 테스트
   - [ ] 데이터베이스 백업 설정 확인
   - [ ] 도메인 DNS 설정 확인
   - [ ] SSL 인증서 검증 완료

## 🎉 장점

| 항목 | 설명 |
|------|------|
| **간단함** | 4줄 설정으로 즉시 배포 |
| **자동화** | 80% 이상 자동 감지 |
| **안전함** | VPN 접근 제어, HTTPS 자동 |
| **최적화** | 환경별 리소스 자동 조정 |
| **유연함** | 필요시 모든 설정 재정의 가능 |

---

**Happy Deploying! 🚀**
