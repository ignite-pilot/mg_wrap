"""AWS Secrets Manager 유틸리티 모듈"""
import json
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Optional, Any


def get_secret(secret_name: str, region_name: str = 'ap-northeast-2') -> Optional[Dict[str, Any]]:
    """
    AWS Secrets Manager에서 시크릿 값을 가져옵니다.
    
    Args:
        secret_name: Secrets Manager의 시크릿 이름 (예: 'prod/ignite-pilot/postgresInfo2')
        region_name: AWS 리전 (기본값: ap-northeast-2)
    
    Returns:
        시크릿 값이 JSON인 경우 파싱된 딕셔너리, 문자열인 경우 그대로 반환
        실패 시 None 반환
    """
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
        
        # JSON 형식인지 확인하고 파싱
        try:
            return json.loads(secret_string)
        except json.JSONDecodeError:
            # JSON이 아니면 문자열로 반환
            return {'value': secret_string}
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            print(f"❌ Secret '{secret_name}' not found in AWS Secrets Manager")
        elif error_code == 'InvalidRequestException':
            print(f"❌ Invalid request for secret '{secret_name}': {e}")
        elif error_code == 'InvalidParameterException':
            print(f"❌ Invalid parameter for secret '{secret_name}': {e}")
        elif error_code == 'DecryptionFailure':
            print(f"❌ Decryption failure for secret '{secret_name}': {e}")
        elif error_code == 'InternalServiceError':
            print(f"❌ Internal service error for secret '{secret_name}': {e}")
        else:
            print(f"❌ Error retrieving secret '{secret_name}': {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error retrieving secret '{secret_name}': {e}")
        return None


def get_github_token() -> Optional[str]:
    """
    AWS Secrets Manager에서 GitHub Personal Access Token을 가져옵니다.
    
    Returns:
        GitHub PAT 문자열, 실패 시 None
    """
    secret = get_secret('prod/ignite-pilot/github')
    if secret:
        # secret이 딕셔너리인 경우 'GITHUB-PAT', 'token', 'value', 'PAT' 키 확인
        if isinstance(secret, dict):
            return secret.get('GITHUB-PAT') or secret.get('token') or secret.get('value') or secret.get('PAT')
        return str(secret)
    return None


def get_postgres_info() -> Optional[Dict[str, Any]]:
    """
    AWS Secrets Manager에서 PostgreSQL 연결 정보를 가져옵니다.
    
    Returns:
        PostgreSQL 연결 정보 딕셔너리 (host, port, user, password 등)
        실패 시 None
    """
    secret = get_secret('prod/ignite-pilot/postgresInfo2')
    if secret and isinstance(secret, dict):
        return secret
    return None


def get_mysql_info() -> Optional[Dict[str, Any]]:
    """
    AWS Secrets Manager에서 MySQL 연결 정보를 가져옵니다.
    
    Returns:
        MySQL 연결 정보 딕셔너리 (host, port, user, password 등)
        실패 시 None
    """
    secret = get_secret('prod/ignite-pilot/mysql-realpilot')
    if secret and isinstance(secret, dict):
        return secret
    return None

