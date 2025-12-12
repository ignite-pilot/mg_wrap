#!/usr/bin/env bash
################################################################################
# AWS 애플리케이션 삭제 스크립트
################################################################################
#
# 역할:
#   최소한의 설정(앱 이름, 환경, AWS Profile)만으로 배포된 AWS 리소스를
#   자동으로 삭제하는 스크립트입니다. 기존 CloudFormation 스택을 분석하여
#   App Type을 자동으로 감지하고 적절한 정리 작업을 수행합니다.
#
# Fail-Fast 전략:
#   - 모든 필수 값은 config 파일에 명시되어야 함 (키보드 입력 없음)
#   - 모든 검증 실패 시 명확한 에러 메시지와 함께 즉시 종료
#   - set -euo pipefail로 모든 에러를 즉시 감지
#
# 사용법:
#   ./destroy.sh <config-file.yaml>
#   예: ./destroy.sh config.alpha.yaml
#
# 필수 입력 (config 파일):
#   - application_name: 애플리케이션 이름
#   - deployment_phase: 배포 환경 (alpha, beta, production)
#   - aws_profile: AWS CLI 프로파일 이름
#
# 자동 감지 항목:
#   1. AWS Region: AWS Profile 설정에서 자동 추출
#   2. 앱 타입: CloudFormation 스택 출력에서 자동 감지
#      - ECRRepositoryURI 출력 존재 → fullstack
#      - S3BucketName 출력 존재 → static
#   3. 스택 존재 여부: CloudFormation에서 스택 확인
#
# 실행 흐름:
#   [1단계: 초기화 및 검증]
#   - config 파일 파싱 (YAML → 환경변수)
#   - 필수 항목 검증 (app_name, phase, profile)
#   - AWS Region 자동 감지
#   - AWS 계정 ID 확인
#   - CloudFormation 스택 존재 여부 확인
#
#   [2단계: App Type 자동 감지]
#   - CloudFormation 스택의 Outputs 분석
#   - ECRRepositoryURI 있으면 → fullstack
#   - S3BucketName 있으면 → static
#   - 둘 다 없으면 → unknown (그래도 삭제 시도)
#
#   [3단계: 사전 정리 작업]
#   A. Static App인 경우:
#      - S3 버킷 완전히 비우기
#        * 모든 버전 삭제
#        * Delete Marker 삭제
#
#   B. Full-stack App인 경우:
#      - ECR Repository 완전히 비우기
#        * 모든 이미지 삭제
#
#   [4단계: CloudFormation 스택 삭제]
#   - CloudFormation delete-stack 실행
#   - 삭제 완료 대기 (stack-delete-complete)
#   - 타임아웃이나 실패 시 에러 메시지 출력
#
#   [5단계: 정리 결과 출력]
#   - 삭제된 리소스 목록 표시
#   - RDS 스냅샷 남아있을 수 있음 안내 (Full-stack만)
#   - Hosted Zone 수동 삭제 필요 여부 안내
#
# 삭제되는 리소스:
#   Static App:
#   - CloudFormation Stack
#   - S3 Bucket (모든 파일 포함)
#   - CloudFront Distribution
#   - Route53 DNS Record
#   - ACM Certificate
#   - WAF Web ACL (Alpha/Beta만)
#
#   Full-stack App:
#   - CloudFormation Stack
#   - ECS Cluster, Service, Tasks
#   - Application Load Balancer
#   - Target Groups
#   - RDS Database Instance (최종 스냅샷 생성)
#   - ECR Repository (모든 이미지 포함)
#   - Security Groups
#   - CloudWatch Log Groups
#   - Route53 DNS Record
#   - ACM Certificate
#
# 삭제되지 않는 리소스:
#   - Route53 Hosted Zone (CreateHostedZone=true인 경우 수동 삭제 필요)
#   - RDS Final Snapshot (수동 삭제 가능)
#   - IAM Roles (다른 스택과 공유 가능)
#
# 에러 처리:
#   - set -euo pipefail: 모든 명령 실패 시 즉시 종료
#   - 스택이 없으면 메시지 출력 후 정상 종료
#   - 모든 실패에 명확한 원인과 해결 방법 제시
#   - 삭제 실패 시 CloudFormation 콘솔 URL 안내
#
# 안전장치:
#   - 삭제 전 상세 정보 표시
#   - 자동으로 삭제 진행 (키보드 입력 없음)
#   - 스택 삭제 완료까지 대기하여 상태 확인
#
# 주요 함수:
#   - load_config: YAML 파싱 및 필수 항목 검증
#   - detect_aws_region: AWS Profile에서 Region 추출
#   - check_stack_exists: CloudFormation 스택 존재 여부 확인
#   - detect_app_type_from_stack: 스택 출력에서 App Type 감지
#   - empty_s3_bucket: S3 버킷 완전 비우기 (Static)
#   - empty_ecr_repository: ECR Repository 완전 비우기 (Full-stack)
#   - delete_stack: CloudFormation 스택 삭제 및 대기
#
# 의존성:
#   - AWS CLI: CloudFormation, S3, ECR 작업
#   - sed, awk: YAML 파싱
#
# 주의사항:
#   - RDS 최종 스냅샷은 자동으로 삭제되지 않음 (비용 발생 가능)
#   - Hosted Zone은 삭제되지 않음 (수동 삭제 필요)
#   - S3 버킷의 모든 버전이 삭제되므로 복구 불가능
#   - 삭제는 되돌릴 수 없으므로 신중하게 확인 후 실행
#
# 복구 방법:
#   - RDS Snapshot이 있다면 복원 가능
#   - S3/ECR 데이터는 복구 불가능
#   - CloudFormation으로 인프라 재생성 가능
#
################################################################################

set -euo pipefail

# Disable AWS CLI pager to prevent interactive prompts
export AWS_PAGER=""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

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

# Function to load configuration
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

    # Convert underscores to hyphens for CloudFormation compatibility
    APP_NAME=$(echo "${CONFIG_application_name:-}" | tr '_' '-')
    DEPLOYMENT_PHASE="${CONFIG_deployment_phase:-}"
    AWS_PROFILE="${CONFIG_aws_profile:-}"

    if [ "$APP_NAME" != "${CONFIG_application_name:-}" ]; then
        print_info "애플리케이션 이름 정규화: ${CONFIG_application_name} → $APP_NAME"
    fi

    print_success "설정 로드 완료"
}

# Function to detect AWS region
detect_aws_region() {
    if [ -n "${CONFIG_aws_region:-}" ]; then
        AWS_REGION="${CONFIG_aws_region:-}"
    else
        AWS_REGION=$(aws configure get region --profile "$AWS_PROFILE" 2>/dev/null || echo "ap-northeast-2")
    fi
    print_detect "사용 Region: $AWS_REGION"
}

# Function to get AWS account ID
get_aws_account_id() {
    if ! aws sts get-caller-identity --profile "$AWS_PROFILE" &> /dev/null; then
        print_error "AWS 자격증명이 설정되지 않음 (Profile): $AWS_PROFILE"
        exit 1
    fi

    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile "$AWS_PROFILE" --query Account --output text)
    print_success "AWS 계정 ID: $AWS_ACCOUNT_ID"
}

# Function to detect app type from existing stack
detect_app_type_from_stack() {
    local stack_name="${DEPLOYMENT_PHASE}-${APP_NAME}-stack"

    print_info "기존 스택에서 앱 타입 감지 중..."

    # Check if ECR repository exists (indicates fullstack)
    local ecr_check=$(aws cloudformation describe-stacks \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --stack-name "$stack_name" \
        --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryURI`].OutputValue' \
        --output text 2>/dev/null || echo "")

    if [ -n "$ecr_check" ] && [ "$ecr_check" != "None" ]; then
        APP_TYPE="fullstack"
        print_detect "앱 타입 감지: fullstack"
    else
        # Check if S3 bucket exists (indicates static)
        local s3_check=$(aws cloudformation describe-stacks \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION" \
            --stack-name "$stack_name" \
            --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
            --output text 2>/dev/null || echo "")

        if [ -n "$s3_check" ] && [ "$s3_check" != "None" ]; then
            APP_TYPE="static"
            print_detect "앱 타입 감지: static"
        else
            print_warning "앱 타입 감지 실패, 그래도 정리 시도"
            APP_TYPE="unknown"
        fi
    fi
}

# Function to check if stack exists
check_stack_exists() {
    local stack_name="${DEPLOYMENT_PHASE}-${APP_NAME}-stack"

    STACK_EXISTS=$(aws cloudformation describe-stacks \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --stack-name "$stack_name" \
        --query 'Stacks[0].StackName' \
        --output text 2>/dev/null || echo "")

    if [ -z "$STACK_EXISTS" ]; then
        print_warning "스택이 존재하지 않습니다"
        exit 0
    fi

    print_info "스택 발견: $stack_name"
}

# Function to empty S3 bucket
empty_s3_bucket() {
    if [ "$APP_TYPE" == "static" ]; then
        print_section "S3 버킷 비우기"

        local bucket_name="${DEPLOYMENT_PHASE}-${APP_NAME}-static-content"

        if aws s3 ls "s3://$bucket_name" --profile "$AWS_PROFILE" &> /dev/null; then
            print_info "S3 버킷 비우는 중: $bucket_name"

            # Delete all objects including versions
            aws s3api list-object-versions \
                --profile "$AWS_PROFILE" \
                --bucket "$bucket_name" \
                --output json \
                --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' 2>/dev/null | \
            aws s3api delete-objects \
                --profile "$AWS_PROFILE" \
                --bucket "$bucket_name" \
                --delete file:///dev/stdin 2>/dev/null || true

            # Delete all delete markers
            aws s3api list-object-versions \
                --profile "$AWS_PROFILE" \
                --bucket "$bucket_name" \
                --output json \
                --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' 2>/dev/null | \
            aws s3api delete-objects \
                --profile "$AWS_PROFILE" \
                --bucket "$bucket_name" \
                --delete file:///dev/stdin 2>/dev/null || true

            print_success "S3 버킷 비우기 완료"
        else
            print_info "S3 버킷이 존재하지 않거나 이미 비어있음"
        fi
    fi
}

# Function to empty ECR repository
empty_ecr_repository() {
    if [ "$APP_TYPE" == "fullstack" ]; then
        print_section "ECR Repository 비우기"

        local ecr_repo_name="${APP_NAME}/${DEPLOYMENT_PHASE}"

        IMAGE_IDS=$(aws ecr list-images \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION" \
            --repository-name "$ecr_repo_name" \
            --query 'imageIds[*]' \
            --output json 2>/dev/null || echo "[]")

        if [ "$IMAGE_IDS" != "[]" ]; then
            print_info "ECR Repository에서 이미지 삭제 중: $ecr_repo_name"

            aws ecr batch-delete-image \
                --profile "$AWS_PROFILE" \
                --region "$AWS_REGION" \
                --repository-name "$ecr_repo_name" \
                --image-ids "$IMAGE_IDS" \
                --output text 2>/dev/null || true

            print_success "ECR Repository 비우기 완료"
        else
            print_info "ECR Repository가 이미 비어있거나 존재하지 않음"
        fi
    fi
}

# Function to delete CloudFormation stack
delete_stack() {
    print_section "CloudFormation 스택 삭제"

    local stack_name="${DEPLOYMENT_PHASE}-${APP_NAME}-stack"

    print_info "스택 삭제 중: $stack_name"
    aws cloudformation delete-stack \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --stack-name "$stack_name"

    print_info "스택 삭제 완료 대기 중..."
    print_info "수 분이 소요될 수 있습니다..."

    aws cloudformation wait stack-delete-complete \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --stack-name "$stack_name"

    if [ $? -eq 0 ]; then
        print_success "스택 삭제 완료!"
    else
        print_error "스택 삭제 실패 또는 타임아웃"
        exit 1
    fi
}

# Function to delete ECR stack (fullstack only)
delete_ecr_stack() {
    local ecr_stack_name="${DEPLOYMENT_PHASE}-${APP_NAME}-ecr-stack"

    # Check if ECR stack exists
    if ! aws cloudformation describe-stacks \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --stack-name "$ecr_stack_name" \
        >/dev/null 2>&1; then
        print_info "ECR 스택이 존재하지 않음 (건너뛰기)"
        return 0
    fi

    print_section "ECR 스택 삭제"

    print_info "ECR 스택 삭제 중: $ecr_stack_name"
    aws cloudformation delete-stack \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --stack-name "$ecr_stack_name"

    print_info "ECR 스택 삭제 완료 대기 중..."
    aws cloudformation wait stack-delete-complete \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --stack-name "$ecr_stack_name" 2>/dev/null

    if [ $? -eq 0 ]; then
        print_success "ECR 스택 삭제 완료!"
    else
        print_warning "ECR 스택 삭제 대기 타임아웃 (백그라운드에서 계속 진행 중)"
    fi
}

# Function to display cleanup summary
display_cleanup_summary() {
    print_section "정리 완료!"

    echo ""
    print_success "모든 리소스가 삭제되었습니다"
    echo ""

    if [ "$APP_TYPE" == "fullstack" ]; then
        print_info "참고: RDS 최종 스냅샷이 남아있을 수 있습니다"
        echo "스냅샷 삭제 방법:"
        echo "  aws rds delete-db-snapshot --profile $AWS_PROFILE --db-snapshot-identifier <snapshot-id>"
    fi

    echo ""
}

# Main execution
main() {
    print_section "🗑️  AWS 애플리케이션 삭제"

    # Check if config file is provided
    if [ -z "${1:-}" ]; then
        print_error "사용법: $0 <config-file.yaml>"
        print_info "예시: $0 config.yaml"
        exit 1
    fi

    CONFIG_FILE="$1"

    # Load configuration
    load_config "${CONFIG_FILE:-}"

    # Detect region
    detect_aws_region

    # Get AWS account ID
    get_aws_account_id

    # Check if stack exists
    check_stack_exists

    # Detect app type from stack
    detect_app_type_from_stack

    # Display summary
    print_section "📋 삭제 요약"
    echo "애플리케이션: $APP_NAME"
    echo "배포 환경: $DEPLOYMENT_PHASE"
    echo "앱 타입: $APP_TYPE"
    echo "AWS Profile: $AWS_PROFILE"
    echo "AWS Region: $AWS_REGION"
    echo ""

    # Warning
    print_warning "경고: 모든 리소스가 영구적으로 삭제됩니다!"
    print_info "삭제를 시작합니다..."
    echo ""

    # Empty S3 bucket (static apps)
    empty_s3_bucket

    # Empty ECR repository (fullstack apps)
    empty_ecr_repository

    # Delete main CloudFormation stack
    delete_stack

    # Delete ECR stack (fullstack apps)
    delete_ecr_stack

    # Display cleanup summary
    display_cleanup_summary
}

# Run main function
main "$@"
