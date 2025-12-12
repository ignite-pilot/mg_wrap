#!/usr/bin/env python3
"""GitHub 저장소 생성 및 코드 푸시 스크립트"""
import subprocess
import sys
import os
import json
import boto3
from botocore.exceptions import ClientError

# app 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_secret(secret_name: str, region_name: str = 'ap-northeast-2'):
    """AWS Secrets Manager에서 시크릿 값을 가져옵니다."""
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        
        secret_string = get_secret_value_response.get('SecretString', '')
        
        try:
            return json.loads(secret_string)
        except json.JSONDecodeError:
            return {'value': secret_string}
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"❌ Error retrieving secret '{secret_name}': {error_code} - {error_msg}")
        if error_code == 'ResourceNotFoundException':
            print(f"   Secret '{secret_name}' not found. Please check the secret name.")
        elif error_code == 'AccessDeniedException':
            print(f"   Access denied. Please check AWS credentials and permissions.")
        return None
    except Exception as e:
        print(f"❌ Unexpected error retrieving secret '{secret_name}': {e}")
        import traceback
        traceback.print_exc()
        return None

def get_github_token():
    """AWS Secrets Manager에서 GitHub Personal Access Token을 가져옵니다."""
    secret = get_secret('prod/ignite-pilot/github')
    if secret:
        if isinstance(secret, dict):
            return secret.get('GITHUB-PAT') or secret.get('token') or secret.get('value') or secret.get('PAT')
        return str(secret)
    return None

def create_github_repo(repo_name: str, github_token: str, description: str = ""):
    """GitHub에 새 저장소 생성"""
    import requests
    
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'name': repo_name,
        'description': description,
        'private': False,
        'auto_init': False
    }
    
    try:
        response = requests.post(
            'https://api.github.com/user/repos',
            headers=headers,
            json=data
        )
        response.raise_for_status()
        repo_info = response.json()
        return repo_info.get('clone_url')
    except requests.exceptions.RequestException as e:
        print(f"❌ GitHub 저장소 생성 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"응답: {e.response.text}")
        return None

def main():
    print("🔐 AWS Secrets Manager에서 GitHub 토큰 가져오는 중...")
    github_token = get_github_token()
    
    if not github_token:
        print("❌ GitHub 토큰을 가져올 수 없습니다.")
        sys.exit(1)
    
    print("✅ GitHub 토큰을 성공적으로 가져왔습니다.")
    
    # 저장소 이름 결정 (프로젝트 이름 사용)
    repo_name = "mg_wrap"
    
    print(f"\n📦 GitHub 저장소 '{repo_name}' 생성 중...")
    clone_url = create_github_repo(
        repo_name=repo_name,
        github_token=github_token,
        description="맡길랩 엔터프라이즈 웹 서비스"
    )
    
    if not clone_url:
        print("❌ 저장소 생성에 실패했습니다.")
        sys.exit(1)
    
    print(f"✅ 저장소가 성공적으로 생성되었습니다: {clone_url}")
    
    # 기존 원격 저장소 확인
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            check=True
        )
        existing_remote = result.stdout.strip()
        print(f"\n현재 원격 저장소: {existing_remote}")
        
        # 원격 저장소 변경
        subprocess.run(['git', 'remote', 'set-url', 'origin', clone_url], check=True)
        print(f"✅ 원격 저장소를 새 저장소로 변경했습니다: {clone_url}")
    except subprocess.CalledProcessError:
        # 원격 저장소가 없으면 추가
        subprocess.run(['git', 'remote', 'add', 'origin', clone_url], check=True)
        print(f"✅ 원격 저장소를 추가했습니다: {clone_url}")
    
    # 변경사항 스테이징
    print("\n📝 변경사항 스테이징 중...")
    subprocess.run(['git', 'add', '-A'], check=True)
    
    # 커밋
    print("💾 커밋 중...")
    try:
        subprocess.run(
            ['git', 'commit', '-m', 'Migrate to AWS Secrets Manager and update DB name to ig-board'],
            check=True
        )
        print("✅ 커밋 완료")
    except subprocess.CalledProcessError as e:
        if 'nothing to commit' in str(e):
            print("⚠️  커밋할 변경사항이 없습니다.")
        else:
            print(f"❌ 커밋 실패: {e}")
            sys.exit(1)
    
    # 원격 URL에 토큰 포함하여 설정
    auth_url = clone_url.replace('https://', f'https://{github_token}@')
    subprocess.run(['git', 'remote', 'set-url', 'origin', auth_url], check=True)
    print(f"✅ 원격 저장소 URL에 인증 정보 추가 완료")
    
    # 푸시
    print("\n🚀 GitHub에 푸시 중...")
    try:
        subprocess.run(
            ['git', 'push', '-u', 'origin', 'main'],
            check=True,
            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
        )
        print("✅ 푸시 완료!")
        print(f"\n🎉 저장소 URL: {clone_url}")
        
        # 보안을 위해 원격 URL에서 토큰 제거 (일반 URL로 변경)
        subprocess.run(['git', 'remote', 'set-url', 'origin', clone_url], check=True)
        print("✅ 원격 저장소 URL에서 인증 정보 제거 완료 (보안)")
    except subprocess.CalledProcessError as e:
        print(f"❌ 푸시 실패: {e}")
        print("\n수동으로 푸시하려면:")
        print(f"  git remote set-url origin {auth_url}")
        print(f"  git push -u origin main")
        sys.exit(1)

if __name__ == "__main__":
    main()

