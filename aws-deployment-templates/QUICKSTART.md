# 빠른 시작 가이드

5분 안에 첫 번째 애플리케이션을 배포하는 방법입니다.

## 사전 준비

1. **AWS CLI 설치 및 설정**
   ```bash
   aws configure --profile default
   ```

2. **Docker 설치** (Full-stack 앱만 필요)
   ```bash
   docker --version
   ```

## Static 웹사이트 배포 (React/Vue/Angular)

### 1단계: 프로젝트 빌드
```bash
cd your-react-project
npm run build
```

### 2단계: 설정 파일 생성
```bash
cd aws-deployment-templates
cp config.yaml config.alpha.yaml
```

### 3단계: 설정 파일 수정 (4줄만!)
```yaml
application_name: "my-website"  # 본인의 앱 이름
deployment_phase: "alpha"
aws_profile: "default"          # 본인의 AWS profile
root_domain: "ig-pilot.com"
```

### 4단계: 배포
```bash
./scripts/deploy.sh config.alpha.yaml
```

**자동으로 감지됨:**
- ✅ App Type: `static` (build/ 폴더 발견)
- ✅ Source Directory: `./build`
- ✅ AWS Region: `ap-northeast-2` (profile에서)
- ✅ Hosted Zone 자동 검색
- ✅ VPN CIDR 자동 추출

### 5단계: 접속
배포 완료 후 표시되는 URL:
- `https://alpha.my-website.ig-pilot.com` (VPN 필수)

---

## Full-Stack 애플리케이션 배포 (Node.js/Python + DB)

### 1단계: Dockerfile 확인
프로젝트 루트에 `Dockerfile`이 있는지 확인:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5000
CMD ["npm", "start"]
```

### 2단계: 설정 파일 생성
```bash
cd aws-deployment-templates
cp config.yaml config.alpha.yaml
```

### 3단계: 설정 파일 수정 (4줄만!)
```yaml
application_name: "my-api"      # 본인의 앱 이름
deployment_phase: "alpha"
aws_profile: "default"          # 본인의 AWS profile
root_domain: "ig-pilot.com"
```

### 4단계: 배포
```bash
# DB 비밀번호 설정 (환경 변수)
export DB_PASSWORD='your-secure-password'

# 배포 실행
cd your-application-root
../aws-deployment-templates/scripts/deploy.sh \
  ../aws-deployment-templates/config.alpha.yaml
```

**자동으로 감지됨:**
- ✅ App Type: `fullstack` (Dockerfile 발견)
- ✅ Container Port: `5000` (Dockerfile EXPOSE)
- ✅ VPC: `vpc-xxx` (dev/ignite 검색)
- ✅ Public Subnets 자동 검색
- ✅ Private Subnets 자동 검색
- ✅ VPC CIDR 자동 추출
- ✅ VPN CIDR 자동 추출
- ✅ Hosted Zone 자동 검색

### 5단계: 접속
배포 완료 후 표시되는 URL:
- `https://alpha.my-api.ig-pilot.com` (VPN 필수)

---

## Production 배포

Alpha에서 충분히 테스트한 후:

### 1단계: 설정 파일 복사
```bash
cp config.alpha.yaml config.prod.yaml
```

### 2단계: deployment_phase 변경
```yaml
deployment_phase: "production"  # alpha → production
```

### 3단계: 배포
```bash
./scripts/deploy.sh config.prod.yaml
```

**자동으로 달라지는 것:**
- ✅ 도메인: `my-api.ig-pilot.com` (phase prefix 없음)
- ✅ 접근: 인터넷 공개 (VPN 불필요)
- ✅ 리소스: db.t3.small (Multi-AZ), 2 vCPU, 4GB, 2+ tasks
- ✅ 백업: 7일 보관

---

## 삭제

필요 없어진 리소스 삭제:
```bash
./scripts/destroy.sh config.alpha.yaml
```

확인 프롬프트:
```
경고: 모든 리소스가 영구적으로 삭제됩니다!
삭제를 확인하려면 'yes'를 입력하세요: yes
```

---

## 주요 명령어 요약

```bash
# Static App 배포
./scripts/deploy.sh config.alpha.yaml

# Full-Stack App 배포
./scripts/deploy.sh config.alpha.yaml
# (DB 비밀번호 입력 프롬프트)

# 리소스 삭제
./scripts/destroy.sh config.alpha.yaml

# 로그 확인 (Full-Stack)
aws logs tail /ecs/alpha-{app-name} --follow

# 스택 상태 확인
aws cloudformation describe-stacks \
  --stack-name alpha-{app-name}-stack
```

---

## 자동 감지 vs 수동 지정

### 자동 감지 (권장)
```yaml
# 최소 4줄
application_name: "my-app"
deployment_phase: "alpha"
aws_profile: "default"
root_domain: "ig-pilot.com"
```

### 필요시 수동 지정
```yaml
# 최소 4줄
application_name: "my-app"
deployment_phase: "alpha"
aws_profile: "default"
root_domain: "ig-pilot.com"

# 자동 감지 재정의
app_type: "fullstack"
aws_region: "us-east-1"

vpc:
  vpc_id: "vpc-custom-123"

container_port: 3000
```

---

## 팁

1. **Alpha 먼저 테스트**: 항상 Alpha 환경에서 먼저 테스트 후 Production으로 이동
2. **비밀번호 안전하게**: 설정 파일에 비밀번호 하드코딩 금지
3. **VPN 연결**: Alpha/Beta는 VPN 연결 필수
4. **로그 확인**: 문제 발생 시 CloudWatch Logs 먼저 확인
5. **환경별 파일**: `config.alpha.yaml`, `config.beta.yaml`, `config.prod.yaml` 별도 관리

---

## 다음 단계

- [README.md](README.md) - 전체 기능 및 상세 가이드
- [config.yaml](config.yaml) - 모든 설정 옵션 및 예제 (주석 포함)

---

**Happy Deploying! 🚀**
