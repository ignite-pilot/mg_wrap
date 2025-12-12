#!/usr/bin/env bash
################################################################################
# AWS 애플리케이션 배포 스크립트
################################################################################
#
# 역할:
#   최소한의 설정(앱 이름, 환경, AWS Profile, 도메인)만으로 AWS에 애플리케이션을
#   자동으로 배포하는 스크립트입니다. 애플리케이션 타입, VPC, Subnet 등 대부분의
#   인프라 정보를 자동으로 감지하여 사람의 수동 입력을 최소화합니다.
#
# Fail-Fast 전략:
#   - 모든 필수 값은 config 파일에 명시되어야 함 (키보드 입력 없음)
#   - 모든 검증 실패 시 명확한 에러 메시지와 함께 즉시 종료
#   - set -euo pipefail로 모든 에러를 즉시 감지
#
# 사용법:
#   ./deploy.sh <config-file.yaml>
#   예: ./deploy.sh config.alpha.yaml
#
# 필수 입력 (config 파일):
#   - application_name: 애플리케이션 이름
#   - deployment_phase: 배포 환경 (alpha, beta, production)
#   - aws_profile: AWS CLI 프로파일 이름
#   - root_domain: 루트 도메인 (예: ig-pilot.com)
#   - db_password: (Full-stack + DB 활성화 시) 데이터베이스 비밀번호 (최소 8자)
#
# 자동 감지 항목:
#   1. 앱 타입: Dockerfile 존재 → fullstack, dist/build 폴더 → static
#   2. AWS Region: AWS Profile 설정에서 자동 추출
#   3. VPC: 'dev' 또는 'ignite' 이름 포함된 VPC 우선 검색
#   4. Public Subnets: 태그 이름에 'public' 포함된 서브넷 검색
#   5. Private Subnets: 태그 이름에 'private' 포함된 서브넷 검색
#   6. VPC CIDR: VPC 정보에서 자동 추출
#   7. VPN CIDR: Client VPN Endpoint에서 자동 추출 (없으면 10.255.0.0/16)
#   8. Hosted Zone: 도메인명으로 Route53에서 검색 (없으면 자동 생성)
#   9. 컨테이너 포트: Dockerfile의 EXPOSE 지시어에서 추출 (기본값: 5000)
#  10. Health Check Path: 기본값 /health
#  11. Database Config: PostgreSQL, app_admin, app_db (변경 가능)
#
# 실행 흐름:
#   [1단계: 초기화 및 설정 로드]
#   - config 파일 파싱 (YAML → 환경변수)
#   - 필수 항목 검증 (app_name, phase, profile, domain)
#
#   [2단계: 자동 감지]
#   - App Type 감지: Dockerfile, dist/, build/, public/ 폴더 확인
#   - AWS Region 감지: AWS Profile에서 region 추출
#   - AWS 인프라 검색:
#     * VPC 검색 (dev/ignite 키워드 우선)
#     * Public/Private Subnet 검색 (태그 기반)
#     * VPC CIDR 추출
#     * VPN CIDR 추출 (Client VPN Endpoint)
#     * Hosted Zone 검색 (도메인 기반)
#   - Container 설정 감지:
#     * Dockerfile에서 EXPOSE 포트 추출
#     * Health check path 설정
#   - Database 설정:
#     * 활성화 여부 확인
#     * 비밀번호 입력 프롬프트 (없는 경우)
#
#   [3단계: 배포 실행]
#   A. Static App인 경우:
#      - CloudFormation 스택 배포 (S3 + CloudFront + Route53)
#      - 정적 파일 S3 업로드
#      - CloudFront 캐시 무효화
#
#   B. Full-stack App인 경우:
#      - Docker 이미지 빌드
#      - ECR 로그인 및 이미지 푸시 (실패 시 나중에 재시도)
#      - CloudFormation 스택 배포 (ECS + RDS + ALB + Route53)
#      - ECR 이미지 푸시 재시도 (필요한 경우)
#      - ECS 서비스 강제 재배포
#
#   [4단계: 결과 출력]
#   - CloudFormation 스택 출력 정보 표시
#   - 애플리케이션 접속 URL 표시
#   - 다음 단계 안내 (로그 확인, 서비스 상태 등)
#
# 접근 제어:
#   - Alpha/Beta: VPN CIDR에서만 접근 가능 (Security Group/WAF)
#   - Production: 인터넷 공개 접근
#
# 도메인 패턴:
#   - Alpha: alpha.{app-name}.{root-domain}
#   - Beta: beta.{app-name}.{root-domain}
#   - Production: {app-name}.{root-domain}
#
# 리소스 크기 (자동 조정):
#   Alpha/Beta: db.t3.micro, 1 vCPU, 2GB RAM, FARGATE_SPOT
#   Production: db.t3.small (Multi-AZ), 2 vCPU, 4GB RAM, FARGATE
#
# 에러 처리:
#   - set -e: 모든 명령 실패 시 즉시 종료
#   - 각 단계별 검증 및 에러 메시지 출력
#   - CloudFormation 배포 실패 시 이벤트 로그 확인 안내
#
# 주요 함수:
#   - load_config: YAML 파싱 및 필수 항목 검증
#   - detect_app_type: Dockerfile, 빌드 폴더로 앱 타입 판단
#   - detect_aws_region: AWS Profile에서 Region 추출
#   - discover_aws_infrastructure: VPC, Subnet, Zone 자동 검색
#   - detect_container_port: Dockerfile EXPOSE 파싱
#   - build_and_push_image: Docker 빌드 및 ECR 푸시
#   - deploy_cloudformation: CloudFormation 스택 배포
#   - upload_static_files: S3 업로드 (Static 앱)
#   - update_ecs_service: ECS 강제 재배포 (Full-stack 앱)
#
# 의존성:
#   - AWS CLI: VPC, Subnet, Route53 정보 조회
#   - Docker: 이미지 빌드 및 푸시 (Full-stack만)
#   - sed, awk: YAML 파싱
#
# 주의사항:
#   - VPC와 Subnet은 태그 이름으로 검색하므로 명명 규칙 중요
#   - 여러 VPC가 있을 경우 'dev' 또는 'ignite' 포함된 것 우선 선택
#   - ECR Repository는 CloudFormation이 생성하므로 첫 푸시 실패는 정상
#   - 데이터베이스 비밀번호는 config 파일에 필수로 지정해야 함 (최소 8자)
#
################################################################################

set -euo pipefail

# Disable AWS CLI pager to prevent interactive prompts
export AWS_PAGER=""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATES_DIR="$PROJECT_ROOT/cloudformation"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output with timestamp
get_timestamp() { date '+%Y-%m-%d %H:%M:%S'; }
print_info() { echo -e "[$(get_timestamp)] ${BLUE}ℹ${NC} $1"; }
print_success() { echo -e "[$(get_timestamp)] ${GREEN}✓${NC} $1"; }
print_warning() { echo -e "[$(get_timestamp)] ${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "[$(get_timestamp)] ${RED}✗${NC} $1"; }
print_detect() { echo -e "[$(get_timestamp)] ${CYAN}🔍${NC} $1"; }
print_section() {
    echo ""
    echo "[$(get_timestamp)] ========================================="
    echo "[$(get_timestamp)] $1"
    echo "[$(get_timestamp)] ========================================="
}

# Function to parse YAML (simple key-value parser)
# Handles comments after values and nested keys
parse_yaml() {
    local file=$1
    local prefix=$2

    # Remove comment lines and empty lines, then parse
    grep -v '^[[:space:]]*#' "$file" | grep -v '^[[:space:]]*$' | \
    awk -v prefix="$prefix" '
    BEGIN {
        FS = ":"
    }
    {
        # Skip comment lines
        if ($0 ~ /^[[:space:]]*#/) next

        # Calculate indent level
        indent = match($0, /[^[:space:]]/)-1
        if (indent < 0) indent = 0
        indent_level = int(indent/2)

        # Extract key
        gsub(/^[[:space:]]+/, "", $1)
        key = $1

        # Skip if no key
        if (key == "") next

        # Store key at current level
        keys[indent_level] = key

        # Clear deeper levels
        for (i = indent_level+1; i < 10; i++) {
            delete keys[i]
        }

        # Extract value (everything after first colon)
        value = substr($0, index($0, ":")+1)

        # Remove leading/trailing whitespace
        gsub(/^[[:space:]]+/, "", value)
        gsub(/[[:space:]]+$/, "", value)

        # Remove trailing comments
        gsub(/[[:space:]]*#.*$/, "", value)
        gsub(/[[:space:]]+$/, "", value)

        # Remove quotes if present
        gsub(/^["'"'"']/, "", value)
        gsub(/["'"'"']$/, "", value)

        # If value is not empty, print the variable
        if (value != "") {
            # Build full key path
            fullkey = ""
            for (i = 0; i < indent_level; i++) {
                if (keys[i] != "") {
                    fullkey = fullkey keys[i] "_"
                }
            }
            fullkey = fullkey key

            printf("%s%s=\"%s\"\n", prefix, fullkey, value)
        }
    }
    '
}

# Function to load minimal configuration
load_config() {
    local config_file=$1

    if [ ! -f "$config_file" ]; then
        print_error "설정 파일을 찾을 수 없습니다: $config_file"
        exit 1
    fi

    print_info "설정 파일 로드 중: $config_file"
    eval $(parse_yaml "$config_file" "CONFIG_")

    # Validate required fields
    if [ -z "${CONFIG_application_name:-}" ]; then
        print_error "설정 파일에 application_name이 필요합니다"
        exit 1
    fi

    if [ -z "${CONFIG_deployment_phase:-}" ]; then
        print_error "설정 파일에 deployment_phase가 필요합니다"
        exit 1
    fi

    if [ -z "${CONFIG_aws_profile:-}" ]; then
        print_error "설정 파일에 aws_profile이 필요합니다"
        exit 1
    fi

    if [ -z "${CONFIG_root_domain:-}" ]; then
        print_error "설정 파일에 root_domain이 필요합니다"
        exit 1
    fi

    # Store basic config (these are already validated as required)
    # Convert underscores to hyphens for CloudFormation compatibility
    APP_NAME=$(echo "$CONFIG_application_name" | tr '_' '-')
    DEPLOYMENT_PHASE="$CONFIG_deployment_phase"
    AWS_PROFILE="$CONFIG_aws_profile"
    ROOT_DOMAIN="$CONFIG_root_domain"
    DB_PASSWORD="${CONFIG_db_password:-}"

    # Validate app name format (CloudFormation requirement)
    if ! [[ "$APP_NAME" =~ ^[a-zA-Z][-a-zA-Z0-9]*$ ]]; then
        print_error "애플리케이션 이름이 CloudFormation 요구사항을 만족하지 않습니다"
        echo ""
        echo "요구사항:"
        echo "  - 알파벳으로 시작해야 함"
        echo "  - 알파벳, 숫자, 하이픈(-)만 사용 가능"
        echo "  - 언더스코어(_)는 자동으로 하이픈(-)으로 변환됨"
        echo ""
        echo "현재 값: $CONFIG_application_name → $APP_NAME"
        exit 1
    fi

    if [ "$APP_NAME" != "$CONFIG_application_name" ]; then
        print_info "애플리케이션 이름 정규화: $CONFIG_application_name → $APP_NAME"
    fi

    print_success "설정 로드 완료"
}

# Function to detect app type
detect_app_type() {
    print_section "애플리케이션 타입 자동 감지"

    # Check if app_type is already specified in config
    if [ -n "${CONFIG_app_type:-}" ]; then
        APP_TYPE="${CONFIG_app_type:-}"
        print_info "설정 파일에 앱 타입 지정됨: $APP_TYPE"
        return
    fi

    # Check for Dockerfile
    if [ -f "Dockerfile" ]; then
        APP_TYPE="fullstack"
        print_detect "Dockerfile 발견 → 앱 타입: fullstack"
        return
    fi

    # Check for common build output directories
    if [ -d "dist" ] || [ -d "build" ] || [ -d "public" ]; then
        APP_TYPE="static"
        if [ -d "dist" ]; then
            STATIC_SOURCE_DIR="./dist"
            print_detect "dist/ 디렉토리 발견 → 앱 타입: static"
        elif [ -d "build" ]; then
            STATIC_SOURCE_DIR="./build"
            print_detect "build/ 디렉토리 발견 → 앱 타입: static"
        elif [ -d "public" ]; then
            STATIC_SOURCE_DIR="./public"
            print_detect "public/ 디렉토리 발견 → 앱 타입: static"
        fi
        return
    fi

    # Fail if app type cannot be detected
    print_error "앱 타입 자동 감지 실패"
    echo ""
    echo "다음 중 하나가 필요합니다:"
    echo "  1. Dockerfile (Full-stack 앱)"
    echo "  2. dist/ 또는 build/ 또는 public/ 폴더 (Static 앱)"
    echo ""
    echo "또는 config 파일에 명시:"
    echo "  app_type: \"static\"  # 또는 \"fullstack\""
    exit 1
}

# Function to auto-detect AWS region
detect_aws_region() {
    print_section "AWS Region 자동 감지"

    # Check if region is specified in config
    if [ -n "${CONFIG_aws_region:-}" ]; then
        AWS_REGION="${CONFIG_aws_region:-}"
        print_info "설정 파일에 Region 지정됨: $AWS_REGION"
        return
    fi

    # Get region from AWS profile
    # Try to get from profile
    AWS_REGION=$(aws configure get region --profile "$AWS_PROFILE" 2>/dev/null || echo "")

    if [ -z "$AWS_REGION" ]; then
        print_error "AWS Region을 감지할 수 없습니다"
        echo ""
        echo "해결 방법:"
        echo "  1. AWS Profile에 Region 설정:"
        echo "     aws configure set region ap-northeast-2 --profile $AWS_PROFILE"
        echo ""
        echo "  2. config 파일에 명시:"
        echo "     aws_region: \"ap-northeast-2\""
        exit 1
    fi

    print_detect "Profile에서 Region 감지: $AWS_REGION"
}

# Function to discover AWS infrastructure
discover_aws_infrastructure() {
    print_section "AWS 인프라 자동 검색"

    # Get AWS Account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile "$AWS_PROFILE" --query Account --output text)
    print_success "AWS 계정 ID: $AWS_ACCOUNT_ID"

    # Only discover VPC info for fullstack apps
    if [ "$APP_TYPE" == "fullstack" ]; then
        discover_vpc_info
    fi

    # Discover Hosted Zone
    discover_hosted_zone
}

# Function to discover VPC information
discover_vpc_info() {
    print_info "VPC 및 Subnet 정보 검색 중..."

    # Check if VPC info is already in config
    if [ -n "${CONFIG_vpc_vpc_id:-}" ]; then
        VPC_ID="${CONFIG_vpc_vpc_id:-}"
        print_info "설정 파일에 VPC ID 지정됨: $VPC_ID"
    else
        # Find VPC (prefer ones with 'dev' or 'ignite' in name)
        VPC_ID=$(aws ec2 describe-vpcs \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION" \
            --filters "Name=tag:Name,Values=*dev*,*ignite*" \
            --query 'Vpcs[0].VpcId' \
            --output text 2>/dev/null || echo "")

        if [ -z "$VPC_ID" ] || [ "$VPC_ID" == "None" ]; then
            # Fallback to any VPC
            VPC_ID=$(aws ec2 describe-vpcs \
                --profile "$AWS_PROFILE" \
                --region "$AWS_REGION" \
                --query 'Vpcs[0].VpcId' \
                --output text 2>/dev/null || echo "")
        fi

        if [ -z "$VPC_ID" ] || [ "$VPC_ID" == "None" ]; then
            print_error "VPC를 찾을 수 없습니다. 설정 파일에 vpc_id를 지정해주세요."
            exit 1
        fi

        print_detect "VPC 발견: $VPC_ID"
    fi

    # Get VPC CIDR
    VPC_CIDR=$(aws ec2 describe-vpcs \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --vpc-ids "$VPC_ID" \
        --query 'Vpcs[0].CidrBlock' \
        --output text)
    print_detect "VPC CIDR: $VPC_CIDR"

    # Discover Public Subnets
    if [ -n "${CONFIG_vpc_public_subnet_ids:-}" ]; then
        PUBLIC_SUBNET_IDS="${CONFIG_vpc_public_subnet_ids:-}"
        print_info "설정 파일에 Public Subnet 지정됨"
    else
        # Try multiple patterns: public, pub, Public, Pub
        PUBLIC_SUBNET_IDS=$(aws ec2 describe-subnets \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION" \
            --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=*public*,*pub*,*Public*,*Pub*" \
            --query 'Subnets[].SubnetId' \
            --output text | tr '\t' ',')

        if [ -z "$PUBLIC_SUBNET_IDS" ]; then
            print_error "Public Subnet을 찾을 수 없습니다"
            echo ""
            echo "해결 방법:"
            echo "  1. config 파일에 수동으로 지정:"
            echo "     vpc:"
            echo "       public_subnet_ids:"
            echo "         - \"subnet-xxxxx\""
            echo "         - \"subnet-yyyyy\""
            echo ""
            echo "  2. 서브넷 태그 이름에 'public' 또는 'pub' 포함"
            exit 1
        fi

        print_detect "Public Subnet 발견: $PUBLIC_SUBNET_IDS"
    fi

    # Discover Private Subnets
    if [ -n "${CONFIG_vpc_private_subnet_ids:-}" ]; then
        PRIVATE_SUBNET_IDS="${CONFIG_vpc_private_subnet_ids:-}"
        print_info "설정 파일에 Private Subnet 지정됨"
    else
        # Try multiple patterns: private, pri, Private, Pri
        PRIVATE_SUBNET_IDS=$(aws ec2 describe-subnets \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION" \
            --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=*private*,*pri*,*Private*,*Pri*" \
            --query 'Subnets[].SubnetId' \
            --output text | tr '\t' ',')

        if [ -z "$PRIVATE_SUBNET_IDS" ]; then
            print_error "Private Subnet을 찾을 수 없습니다"
            echo ""
            echo "해결 방법:"
            echo "  1. config 파일에 수동으로 지정:"
            echo "     vpc:"
            echo "       private_subnet_ids:"
            echo "         - \"subnet-aaaaa\""
            echo "         - \"subnet-bbbbb\""
            echo ""
            echo "  2. 서브넷 태그 이름에 'private' 또는 'pri' 포함"
            exit 1
        fi

        print_detect "Private Subnet 발견: $PRIVATE_SUBNET_IDS"
    fi

    # Discover VPN CIDR from Client VPN Endpoint
    VPN_CIDR=$(aws ec2 describe-client-vpn-endpoints \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --query 'ClientVpnEndpoints[0].ClientCidrBlock' \
        --output text 2>/dev/null || echo "10.255.0.0/16")

    if [ "$VPN_CIDR" == "None" ] || [ -z "$VPN_CIDR" ]; then
        VPN_CIDR="10.255.0.0/16"
        print_info "VPN CIDR 기본값 사용: $VPN_CIDR"
    else
        print_detect "VPN CIDR 발견: $VPN_CIDR"
    fi
}

# Function to discover Hosted Zone
discover_hosted_zone() {
    print_info "Route53 Hosted Zone 검색 중..."

    # Check if hosted zone is specified in config
    if [ -n "${CONFIG_domain_hosted_zone_id:-}" ]; then
        HOSTED_ZONE_ID="${CONFIG_domain_hosted_zone_id:-}"
        print_info "설정 파일에 Hosted Zone ID 지정됨: $HOSTED_ZONE_ID"
        return
    fi

    # Find hosted zone by domain name
    HOSTED_ZONE_ID=$(aws route53 list-hosted-zones \
        --profile "$AWS_PROFILE" \
        --query "HostedZones[?Name=='${ROOT_DOMAIN}.'].Id" \
        --output text | cut -d'/' -f3)

    if [ -z "$HOSTED_ZONE_ID" ] || [ "$HOSTED_ZONE_ID" == "None" ]; then
        print_info "도메인에 대한 Hosted Zone을 찾을 수 없음: $ROOT_DOMAIN"
        print_info "배포 중 새 Hosted Zone 생성 예정"
        CREATE_HOSTED_ZONE="true"
    else
        print_detect "Hosted Zone 발견: $HOSTED_ZONE_ID"
        CREATE_HOSTED_ZONE="false"
    fi
}

# Function to detect container port from Dockerfile
detect_container_port() {
    if [ "$APP_TYPE" == "fullstack" ] && [ -f "Dockerfile" ]; then
        # Check if port is specified in config
        if [ -n "${CONFIG_container_port:-}" ]; then
            CONTAINER_PORT="${CONFIG_container_port:-}"
            return
        fi

        # Extract EXPOSE directive from Dockerfile
        CONTAINER_PORT=$(grep -i "^EXPOSE" Dockerfile | head -1 | awk '{print $2}' | tr -d '\r')

        if [ -z "$CONTAINER_PORT" ]; then
            CONTAINER_PORT="5000"
            print_info "Dockerfile에 EXPOSE가 없음, 기본 포트 사용: $CONTAINER_PORT"
        else
            print_detect "Dockerfile에서 컨테이너 포트 감지: $CONTAINER_PORT"
        fi
    fi
}

# Function to detect health check path
detect_health_check_path() {
    if [ "$APP_TYPE" == "fullstack" ]; then
        # Check if specified in config
        if [ -n "${CONFIG_health_check_path:-}" ]; then
            HEALTH_CHECK_PATH="${CONFIG_health_check_path:-}"
        else
            HEALTH_CHECK_PATH="/health"
            print_info "기본 Health Check 경로 사용: $HEALTH_CHECK_PATH"
        fi
    fi
}

# Function to detect database configuration
detect_database_config() {
    if [ "$APP_TYPE" == "fullstack" ]; then
        # Check if database is disabled in config
        if [ "${CONFIG_database_enabled:-}" == "false" ]; then
            DATABASE_ENABLED="false"
            print_info "설정에서 데이터베이스 비활성화됨"
            return
        fi

        DATABASE_ENABLED="true"
        DATABASE_ENGINE="${CONFIG_database_engine:-postgres}"
        DATABASE_USERNAME="${CONFIG_database_username:-app_admin}"
        DATABASE_NAME="${CONFIG_database_database_name:-app_db}"

        # Validate database password (REQUIRED in config file)
        if [ -z "$DB_PASSWORD" ]; then
            print_error "데이터베이스 비밀번호가 config 파일에 지정되지 않았습니다"
            echo ""
            echo "해결 방법:"
            echo "  1. config 파일에 다음 추가:"
            echo "     db_password: \"your-secure-password\""
            echo ""
            echo "  2. 환경 변수로 전달:"
            echo "     export DB_PASSWORD='your-secure-password'"
            echo "     ./scripts/deploy.sh config.yaml"
            echo ""
            echo "주의: 비밀번호는 최소 8자 이상이어야 합니다"
            exit 1
        fi

        # Validate password length
        if [ ${#DB_PASSWORD} -lt 8 ]; then
            print_error "데이터베이스 비밀번호는 최소 8자 이상이어야 합니다 (현재: ${#DB_PASSWORD}자)"
            exit 1
        fi
    fi
}

# Function to deploy ECR stack (fullstack only)
deploy_ecr_stack() {
    print_section "ECR Repository 스택 배포"

    local stack_name="${DEPLOYMENT_PHASE}-${APP_NAME}-ecr-stack"
    local template_file="$TEMPLATES_DIR/ecr-repository.yaml"

    # Check if template exists
    if [ ! -f "$template_file" ]; then
        print_error "ECR 템플릿을 찾을 수 없음: $template_file"
        exit 1
    fi

    print_info "스택 이름: $stack_name"
    print_info "템플릿: $(basename $template_file)"

    # Check if stack already exists
    if aws cloudformation describe-stacks \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --stack-name "$stack_name" \
        >/dev/null 2>&1; then
        print_success "ECR 스택이 이미 존재함 (재사용)"
        return 0
    fi

    # Deploy ECR stack
    print_info "ECR 스택 배포 중..."
    aws cloudformation deploy \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --template-file "$template_file" \
        --stack-name "$stack_name" \
        --parameter-overrides \
            ApplicationName="$APP_NAME" \
            DeploymentPhase="$DEPLOYMENT_PHASE" \
        --no-fail-on-empty-changeset

    print_success "ECR Repository 스택 배포 완료"
}

# Function to build and push Docker image (fullstack only)
build_and_push_image() {
    print_section "Docker 이미지 빌드 및 푸시"

    local ecr_repo_uri="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}/${DEPLOYMENT_PHASE}"
    local image_tag="${DEPLOYMENT_PHASE}-$(date +%Y%m%d-%H%M%S)"

    # Get Docker platform from config, default to linux/amd64 for fullstack apps
    local docker_platform="${CONFIG_docker_platform:-linux/amd64}"

    # Build image
    print_info "Docker 이미지 빌드 중: ${APP_NAME}:${image_tag} (플랫폼: ${docker_platform})"

    if ! docker build --platform "${docker_platform}" -t "${APP_NAME}:${image_tag}" . ; then
        print_error "Docker 이미지 빌드 실패"
        echo ""
        echo "확인 사항:"
        echo "  1. Dockerfile이 현재 디렉토리에 있는지 확인"
        echo "  2. Docker가 실행 중인지 확인 (docker ps)"
        echo "  3. Dockerfile 문법 오류 확인"
        exit 1
    fi
    print_success "Docker 이미지 빌드 완료"

    # Deploy ECR stack BEFORE login and push
    deploy_ecr_stack

    # Login to ECR
    print_info "Amazon ECR 로그인 중"
    aws ecr get-login-password \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" | \
        docker login \
        --username AWS \
        --password-stdin \
        "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

    print_success "ECR 로그인 완료"

    # Tag and push images
    docker tag "${APP_NAME}:${image_tag}" "${ecr_repo_uri}:${image_tag}"
    docker tag "${APP_NAME}:${image_tag}" "${ecr_repo_uri}:latest"

    print_info "푸시 중 ${ecr_repo_uri}:${image_tag}"
    docker push "${ecr_repo_uri}:${image_tag}"

    print_info "푸시 중 ${ecr_repo_uri}:latest"
    docker push "${ecr_repo_uri}:latest"

    print_success "Docker 이미지 푸시 완료"
}

# Function to upload static files to S3 (static only)
upload_static_files() {
    print_section "S3에 정적 파일 업로드"

    local source_dir="${STATIC_SOURCE_DIR}"
    local bucket_name="${DEPLOYMENT_PHASE}-${APP_NAME}-static-content"

    if [ ! -d "$source_dir" ]; then
        print_error "소스 디렉토리를 찾을 수 없음: $source_dir"
        exit 1
    fi

    print_info "파일 업로드 중: $source_dir to s3://$bucket_name/"
    aws s3 sync "$source_dir" "s3://$bucket_name/" \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --delete

    print_success "정적 파일 업로드 완료"
}

# Function to deploy CloudFormation stack
deploy_cloudformation() {
    print_section "CloudFormation 스택 배포"

    local stack_name="${DEPLOYMENT_PHASE}-${APP_NAME}-stack"
    local template_file=""
    local param_overrides=()

    # Select template based on app type
    if [ "$APP_TYPE" == "static" ]; then
        template_file="$TEMPLATES_DIR/static-app.yaml"

        param_overrides+=(
            "DeploymentPhase=$DEPLOYMENT_PHASE"
            "ApplicationName=$APP_NAME"
            "RootDomain=$ROOT_DOMAIN"
            "CreateHostedZone=${CREATE_HOSTED_ZONE:-false}"
        )

        if [ -n "$HOSTED_ZONE_ID" ]; then
            param_overrides+=("HostedZoneId=$HOSTED_ZONE_ID")
        fi

        if [ -n "$VPN_CIDR" ]; then
            param_overrides+=("VpnCidr=$VPN_CIDR")
        fi

    elif [ "$APP_TYPE" == "fullstack" ]; then
        template_file="$TEMPLATES_DIR/fullstack-app.yaml"

        param_overrides+=(
            "DeploymentPhase=$DEPLOYMENT_PHASE"
            "ApplicationName=$APP_NAME"
            "VpcId=$VPC_ID"
            "VpcCidr=$VPC_CIDR"
            "VpnCidr=$VPN_CIDR"
            "PublicSubnetIds=$PUBLIC_SUBNET_IDS"
            "PrivateSubnetIds=$PRIVATE_SUBNET_IDS"
            "RootDomain=$ROOT_DOMAIN"
            "CreateHostedZone=${CREATE_HOSTED_ZONE:-false}"
            "ContainerPort=$CONTAINER_PORT"
            "HealthCheckPath=$HEALTH_CHECK_PATH"
        )

        if [ -n "$HOSTED_ZONE_ID" ]; then
            param_overrides+=("HostedZoneId=$HOSTED_ZONE_ID")
        fi

        if [ "$DATABASE_ENABLED" == "true" ]; then
            param_overrides+=(
                "DatabaseEnabled=true"
                "DatabaseEngine=$DATABASE_ENGINE"
                "DBUsername=$DATABASE_USERNAME"
                "DBPassword=$DB_PASSWORD"
                "DBName=$DATABASE_NAME"
            )
        else
            param_overrides+=("DatabaseEnabled=false")
        fi
    fi

    # Display deployment info
    print_info "스택 이름: $stack_name"
    print_info "템플릿: $(basename $template_file)"
    echo ""

    # Deploy stack
    print_info "CloudFormation 스택 배포 중... 매우 오래 걸립니다(약 15분 - 1시간). 인내심을 가지세요!"
    aws cloudformation deploy \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --template-file "$template_file" \
        --stack-name "$stack_name" \
        --parameter-overrides "${param_overrides[@]}" \
        --capabilities CAPABILITY_NAMED_IAM

    if [ $? -ne 0 ]; then
        print_error "CloudFormation 스택 배포 실패"
        echo ""
        echo "디버깅 방법:"
        echo "  1. CloudFormation 콘솔에서 실패 이벤트 확인:"
        echo "     https://console.aws.amazon.com/cloudformation"
        echo ""
        echo "  2. AWS CLI로 스택 이벤트 확인:"
        echo "     aws cloudformation describe-stack-events \\"
        echo "       --stack-name ${STACK_NAME} \\"
        echo "       --profile ${AWS_PROFILE} \\"
        echo "       --query 'StackEvents[?ResourceStatus==\`CREATE_FAILED\`]'"
        exit 1
    fi

    print_success "CloudFormation 스택 배포 완료"
}

# Function to retry Docker push
retry_docker_push() {
    if [ "${SKIP_PUSH:-false}" == true ] && [ "$APP_TYPE" == "fullstack" ]; then
        print_section "Docker 이미지 푸시 재시도"

        local ecr_repo_uri="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}/${DEPLOYMENT_PHASE}"

        sleep 5

        print_info "푸시 중 ${ecr_repo_uri}:latest"
        docker push "${ecr_repo_uri}:latest"

        print_success "Docker 이미지 푸시 완료"
    fi
}

# Function to update ECS service
update_ecs_service() {
    if [ "$APP_TYPE" == "fullstack" ]; then
        print_section "ECS 서비스 업데이트"

        local stack_name="${DEPLOYMENT_PHASE}-${APP_NAME}-stack"

        local cluster_name=$(aws cloudformation describe-stacks \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION" \
            --stack-name "$stack_name" \
            --query 'Stacks[0].Outputs[?OutputKey==`ClusterName`].OutputValue' \
            --output text)

        local service_name=$(aws cloudformation describe-stacks \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION" \
            --stack-name "$stack_name" \
            --query 'Stacks[0].Outputs[?OutputKey==`ServiceName`].OutputValue' \
            --output text)

        print_info "서비스 강제 재배포: $service_name"
        aws ecs update-service \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION" \
            --cluster "$cluster_name" \
            --service "$service_name" \
            --force-new-deployment \
            --query 'service.serviceName' \
            --output text > /dev/null

        print_success "ECS 서비스 업데이트 완료"
    fi
}

# Function to invalidate CloudFront cache
invalidate_cloudfront() {
    if [ "$APP_TYPE" == "static" ]; then
        print_section "CloudFront 캐시 무효화"

        local stack_name="${DEPLOYMENT_PHASE}-${APP_NAME}-stack"

        local distribution_id=$(aws cloudformation describe-stacks \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION" \
            --stack-name "$stack_name" \
            --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
            --output text)

        print_info "Distribution 무효화 생성 중: $distribution_id"
        aws cloudfront create-invalidation \
            --profile "$AWS_PROFILE" \
            --distribution-id "$distribution_id" \
            --paths "/*" \
            --query 'Invalidation.Id' \
            --output text > /dev/null

        print_success "CloudFront 캐시 무효화 완료"
    fi
}

# Function to display outputs
display_outputs() {
    print_section "배포 완료!"

    local stack_name="${DEPLOYMENT_PHASE}-${APP_NAME}-stack"

    echo ""
    print_info "스택 출력:"
    aws cloudformation describe-stacks \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --stack-name "$stack_name" \
        --query 'Stacks[0].Outputs[].[OutputKey,OutputValue]' \
        --output table

    echo ""
    print_success "애플리케이션 URL:"
    aws cloudformation describe-stacks \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --stack-name "$stack_name" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
        --output text

    echo ""
}

# Main execution
main() {
    print_section "🚀 AWS 애플리케이션 배포"

    # Check if config file is provided
    if [ -z "${1:-}" ]; then
        print_error "사용법: $0 <config-file.yaml>"
        print_info "예시: $0 config.yaml"
        exit 1
    fi

    CONFIG_FILE="$1"

    # Load minimal configuration
    load_config "${CONFIG_FILE:-}"

    # Auto-detect everything
    detect_app_type
    detect_aws_region
    discover_aws_infrastructure
    detect_container_port
    detect_health_check_path
    detect_database_config

    # Display summary
    print_section "📋 배포 요약"
    echo "애플리케이션: $APP_NAME"
    echo "배포 환경: $DEPLOYMENT_PHASE"
    echo "앱 타입: $APP_TYPE"
    echo "AWS Profile: $AWS_PROFILE"
    echo "AWS Region: $AWS_REGION"
    if [ "$APP_TYPE" == "fullstack" ]; then
        echo "VPC: $VPC_ID"
        echo "컨테이너 포트: $CONTAINER_PORT"
        echo "데이터베이스: ${DATABASE_ENABLED:-false}"
    fi
    echo "도메인: $ROOT_DOMAIN"
    echo ""

    print_info "배포를 시작합니다..."
    echo ""

    # Build and push Docker image (fullstack only)
    if [ "$APP_TYPE" == "fullstack" ]; then
        build_and_push_image
    fi

    # Deploy CloudFormation stack
    deploy_cloudformation

    # Retry Docker push if needed
    retry_docker_push

    # Upload static files (static only)
    if [ "$APP_TYPE" == "static" ]; then
        upload_static_files
        invalidate_cloudfront
    fi

    # Update ECS service (fullstack only)
    update_ecs_service

    # Display outputs
    display_outputs
}

# Run main function
main "$@"
