#!/bin/bash
# 맡길랩 엔터프라이즈 단일 서비스 시작 스크립트

echo "🚀 맡길랩 엔터프라이즈 서비스 시작 중..."

# 프론트엔드 빌드 확인
if [ ! -d "frontend/dist" ] || [ -z "$(ls -A frontend/dist)" ]; then
    echo "📦 프론트엔드 빌드 중..."
    cd frontend
    npm install
    npm run build
    cd ..
    echo "✅ 프론트엔드 빌드 완료"
else
    echo "✅ 프론트엔드 빌드 파일 확인됨"
fi

# Python 의존성 확인
if [ ! -d "venv" ]; then
    echo "📦 Python 가상환경 생성 중..."
    python3 -m venv venv
fi

echo "📦 Python 의존성 설치 중..."
source venv/bin/activate
pip install -r requirements.txt

# 서비스 시작
echo "🌐 서비스 시작: http://localhost:8400"
python run.py

