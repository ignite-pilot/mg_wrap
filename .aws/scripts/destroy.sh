#!/usr/bin/env bash
# MG-Wrap Enterprise Stack Deletion Script
# WARNING: This will delete all resources created by the CloudFormation stack

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parameters
AWS_PROFILE=${1}
ENVIRONMENT=${2:-alpha}

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(alpha|prod)$ ]]; then
  echo -e "${RED}Error: Invalid environment '$ENVIRONMENT'. Must be 'alpha' or 'prod'.${NC}"
  exit 1
fi

# Configuration
APPLICATION_NAME="mg-wrap-enterprise"
STACK_NAME="${ENVIRONMENT}-${APPLICATION_NAME}-stack"
AWS_REGION="ap-northeast-2"

echo "========================================="
echo "MG-Wrap Enterprise Stack Deletion"
echo "========================================="
echo "Environment:     $ENVIRONMENT"
echo "Stack Name:      $STACK_NAME"
echo "AWS Profile:     $AWS_PROFILE"
echo "AWS Region:      $AWS_REGION"
echo "========================================="
echo ""

# Warning
echo -e "${RED}WARNING: This will delete the following resources:${NC}"
echo "  - ECS Cluster, Service, and Tasks"
echo "  - Application Load Balancer and Target Groups"
echo "  - RDS Database (a final snapshot will be created)"
echo "  - ECR Repository and all images"
echo "  - Security Groups"
echo "  - CloudWatch Log Groups"
echo "  - IAM Roles"
echo "  - ACM Certificate (if configured)"
echo "  - Route53 Records (if configured)"
echo ""

# Confirmation
read -p "Are you sure you want to delete the stack '$STACK_NAME'? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^yes$ ]]; then
    echo "Deletion cancelled."
    exit 0
fi

# Check if stack exists
STACK_EXISTS=$(aws cloudformation describe-stacks \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].StackName' \
    --output text 2>/dev/null || echo "")

if [ -z "$STACK_EXISTS" ]; then
    echo -e "${YELLOW}Stack '$STACK_NAME' does not exist.${NC}"
    exit 0
fi

echo "Deleting stack: $STACK_NAME"
echo ""

# Empty ECR repository first (required before deletion)
echo "Emptying ECR repository..."
ECR_REPO_NAME="${APPLICATION_NAME}/${ENVIRONMENT}"

IMAGE_IDS=$(aws ecr list-images \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --repository-name "$ECR_REPO_NAME" \
    --query 'imageIds[*]' \
    --output json 2>/dev/null || echo "[]")

if [ "$IMAGE_IDS" != "[]" ]; then
    aws ecr batch-delete-image \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --repository-name "$ECR_REPO_NAME" \
        --image-ids "$IMAGE_IDS" \
        --output text 2>/dev/null || true
    echo -e "${GREEN}✓${NC} ECR repository emptied"
else
    echo -e "${YELLOW}ECR repository is already empty or does not exist${NC}"
fi

echo ""

# Delete the CloudFormation stack
echo "Deleting CloudFormation stack..."
aws cloudformation delete-stack \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --stack-name "$STACK_NAME"

echo "Waiting for stack deletion to complete..."
echo "This may take several minutes..."
echo ""

aws cloudformation wait stack-delete-complete \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --stack-name "$STACK_NAME"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓${NC} Stack deleted successfully!"
else
    echo ""
    echo -e "${RED}✗${NC} Stack deletion failed or timed out."
    echo "Check the CloudFormation console for details:"
    echo "https://console.aws.amazon.com/cloudformation/home?region=${AWS_REGION}"
    exit 1
fi

echo ""
echo "========================================="
echo "Cleanup Complete!"
echo "========================================="
echo ""
echo "Note: RDS final snapshot may still exist."
echo "To list snapshots:"
echo "  aws rds describe-db-snapshots --profile $AWS_PROFILE --region $AWS_REGION --query 'DBSnapshots[?contains(DBSnapshotIdentifier, \`${ENVIRONMENT}-${APPLICATION_NAME}\`)].DBSnapshotIdentifier'"
echo ""
