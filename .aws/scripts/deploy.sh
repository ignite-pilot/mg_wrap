#!/usr/bin/env bash
# MG-Wrap Enterprise Deployment Script
# This script builds, pushes Docker images, and deploys the application to AWS ECS

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/../cloudformation"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parameters
AWS_PROFILE=${1}
ENVIRONMENT=${2:-alpha}
DB_PASSWORD=${3}

if [ -z "$DB_PASSWORD" ]; then
  echo -e "${RED}Error: Database password is required${NC}"
  echo "Usage: $0 <AWS_PROFILE> <ENVIRONMENT> <DB_PASSWORD> [GOOGLE_CLIENT_ID] [GOOGLE_CLIENT_SECRET] [SECRET_KEY]"
  echo "Example: $0 <YOUR_AWS_PROFILE> alpha 'MySecurePassword123!'"
  exit 1
fi

# Optional OAuth parameters
GOOGLE_CLIENT_ID=${4:-""}
GOOGLE_CLIENT_SECRET=${5:-""}
SECRET_KEY=${6:-""}

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(alpha|prod)$ ]]; then
  echo -e "${RED}Error: Invalid environment '$ENVIRONMENT'. Must be 'alpha' or 'prod'.${NC}"
  exit 1
fi

# Configuration
APPLICATION_NAME="mg-wrap-enterprise"
STACK_NAME="${ENVIRONMENT}-${APPLICATION_NAME}-stack"
TEMPLATE_FILE="$TEMPLATES_DIR/all-in-one.yaml"
AWS_REGION="ap-northeast-2"

# Check if template file exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}Error: Template file not found: $TEMPLATE_FILE${NC}"
    exit 1
fi

echo "========================================="
echo "MG-Wrap Enterprise Deployment"
echo "========================================="
echo "Environment:     $ENVIRONMENT"
echo "Stack Name:      $STACK_NAME"
echo "AWS Profile:     $AWS_PROFILE"
echo "AWS Region:      $AWS_REGION"
echo "Template:        all-in-one.yaml"
echo "========================================="
echo ""

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile "$AWS_PROFILE" --query Account --output text)
echo -e "${GREEN}✓${NC} AWS Account ID: $AWS_ACCOUNT_ID"

# Check if stack exists
STACK_EXISTS=$(aws cloudformation describe-stacks \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].StackName' \
    --output text 2>/dev/null || echo "")

if [ -n "$STACK_EXISTS" ]; then
    echo -e "${YELLOW}Stack already exists. Getting ECR repository URI...${NC}"
    ECR_REPO_URI=$(aws cloudformation describe-stacks \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryURI`].OutputValue' \
        --output text)
else
    echo -e "${YELLOW}Stack does not exist. Will create new infrastructure.${NC}"
    ECR_REPO_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APPLICATION_NAME}/${ENVIRONMENT}"
fi

echo -e "${GREEN}✓${NC} ECR Repository: $ECR_REPO_URI"
echo ""

# =============================================================================
# STEP 1: Build Docker Image
# =============================================================================

echo "========================================="
echo "STEP 1: Building Docker Image"
echo "========================================="

cd "$PROJECT_ROOT"

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}Error: Dockerfile not found in project root${NC}"
    exit 1
fi

IMAGE_TAG="${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"
echo "Building image: ${APPLICATION_NAME}:${IMAGE_TAG}"

docker build -t "${APPLICATION_NAME}:${IMAGE_TAG}" .

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Docker build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker image built successfully"
echo ""

# =============================================================================
# STEP 2: Login to ECR
# =============================================================================

echo "========================================="
echo "STEP 2: Logging in to ECR"
echo "========================================="

aws ecr get-login-password \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" | \
    docker login \
    --username AWS \
    --password-stdin \
    "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ ECR login failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Successfully logged in to ECR"
echo ""

# =============================================================================
# STEP 3: Tag and Push Docker Image to ECR
# =============================================================================

echo "========================================="
echo "STEP 3: Pushing Docker Image to ECR"
echo "========================================="

# Tag image
docker tag "${APPLICATION_NAME}:${IMAGE_TAG}" "${ECR_REPO_URI}:${IMAGE_TAG}"
docker tag "${APPLICATION_NAME}:${IMAGE_TAG}" "${ECR_REPO_URI}:latest"

echo "Pushing ${ECR_REPO_URI}:${IMAGE_TAG}"
docker push "${ECR_REPO_URI}:${IMAGE_TAG}"

if [ $? -ne 0 ]; then
    # If push fails, the repository might not exist yet
    echo -e "${YELLOW}Push failed. Repository might not exist yet. Will be created by CloudFormation.${NC}"
    SKIP_PUSH=true
else
    echo -e "${GREEN}✓${NC} Pushed ${ECR_REPO_URI}:${IMAGE_TAG}"

    echo "Pushing ${ECR_REPO_URI}:latest"
    docker push "${ECR_REPO_URI}:latest"
    echo -e "${GREEN}✓${NC} Pushed ${ECR_REPO_URI}:latest"
fi

echo ""

# =============================================================================
# STEP 4: Deploy CloudFormation Stack
# =============================================================================

echo "========================================="
echo "STEP 4: Deploying CloudFormation Stack"
echo "========================================="

# Build parameter overrides
PARAM_OVERRIDES=(
    "Environment=$ENVIRONMENT"
    "DBPassword=$DB_PASSWORD"
)

if [ -n "$GOOGLE_CLIENT_ID" ]; then
    PARAM_OVERRIDES+=("GoogleClientId=$GOOGLE_CLIENT_ID")
fi

if [ -n "$GOOGLE_CLIENT_SECRET" ]; then
    PARAM_OVERRIDES+=("GoogleClientSecret=$GOOGLE_CLIENT_SECRET")
fi

if [ -n "$SECRET_KEY" ]; then
    PARAM_OVERRIDES+=("SecretKey=$SECRET_KEY")
fi

echo "Deploying stack with parameters:"
for param in "${PARAM_OVERRIDES[@]}"; do
    # Don't print sensitive values
    if [[ $param == *"Password"* ]] || [[ $param == *"Secret"* ]] || [[ $param == *"SecretKey"* ]]; then
        echo "  ${param%%=*}=***"
    else
        echo "  $param"
    fi
done
echo ""

aws cloudformation deploy \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --template-file "$TEMPLATE_FILE" \
    --stack-name "$STACK_NAME" \
    --parameter-overrides "${PARAM_OVERRIDES[@]}" \
    --capabilities CAPABILITY_NAMED_IAM

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ CloudFormation deployment failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓${NC} CloudFormation stack deployed successfully"
echo ""

# =============================================================================
# STEP 5: Push Docker Image (if skipped earlier)
# =============================================================================

if [ "$SKIP_PUSH" = true ]; then
    echo "========================================="
    echo "STEP 5: Pushing Docker Image (Retry)"
    echo "========================================="

    # Wait a bit for ECR repository to be created
    sleep 5

    echo "Pushing ${ECR_REPO_URI}:${IMAGE_TAG}"
    docker push "${ECR_REPO_URI}:${IMAGE_TAG}"

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Docker push failed!${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓${NC} Pushed ${ECR_REPO_URI}:${IMAGE_TAG}"

    echo "Pushing ${ECR_REPO_URI}:latest"
    docker push "${ECR_REPO_URI}:latest"
    echo -e "${GREEN}✓${NC} Pushed ${ECR_REPO_URI}:latest"
    echo ""
fi

# =============================================================================
# STEP 6: Update ECS Service (force new deployment)
# =============================================================================

echo "========================================="
echo "STEP 6: Updating ECS Service"
echo "========================================="

CLUSTER_NAME=$(aws cloudformation describe-stacks \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`ClusterName`].OutputValue' \
    --output text)

SERVICE_NAME=$(aws cloudformation describe-stacks \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`ServiceName`].OutputValue' \
    --output text)

echo "Forcing new deployment for service: $SERVICE_NAME"
aws ecs update-service \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --cluster "$CLUSTER_NAME" \
    --service "$SERVICE_NAME" \
    --force-new-deployment \
    --query 'service.serviceName' \
    --output text

echo -e "${GREEN}✓${NC} ECS service updated"
echo ""

# =============================================================================
# STEP 7: Display Outputs
# =============================================================================

echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""

# Get stack outputs
echo "Stack Outputs:"
aws cloudformation describe-stacks \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[].[OutputKey,OutputValue]' \
    --output table

echo ""
echo -e "${GREEN}Application URL:${NC}"
aws cloudformation describe-stacks \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
    --output text

echo ""
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo "1. Wait a few minutes for ECS tasks to start"
echo "2. Check ECS service status in AWS Console"
echo "3. Access the application using the URL above"
echo "4. If using a custom domain, configure DNS settings"
echo ""
echo "To check service status:"
echo "  aws ecs describe-services --profile $AWS_PROFILE --region $AWS_REGION --cluster $CLUSTER_NAME --services $SERVICE_NAME"
echo ""
echo "To view logs:"
echo "  aws logs tail --profile $AWS_PROFILE --region $AWS_REGION /ecs/${ENVIRONMENT}-${APPLICATION_NAME} --follow"
echo ""
