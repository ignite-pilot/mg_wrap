#!/bin/bash
# Git pre-commit hook
# 코드 커밋 전에 테스트와 보안 체크를 자동으로 실행

echo "🔍 Pre-commit hook: 테스트 및 보안 체크 실행 중..."

# Python 스크립트 실행
python3 run_tests_and_security.py

# 스크립트가 실패하면 커밋 중단
if [ $? -ne 0 ]; then
    echo "❌ 테스트 또는 보안 체크 실패. 커밋이 중단되었습니다."
    echo "위의 오류를 수정한 후 다시 커밋해주세요."
    exit 1
fi

echo "✅ 모든 체크 통과! 커밋을 진행합니다."
exit 0

