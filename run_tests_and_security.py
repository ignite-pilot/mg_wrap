#!/usr/bin/env python3
"""
자동화된 테스트 및 보안 체크 스크립트
코드 수정 후 자동으로 실행되어 테스트와 보안 체크를 수행합니다.
"""
import subprocess
import sys
import re
from pathlib import Path

# 색상 출력
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def run_command(cmd, description):
    """명령어 실행 및 결과 반환"""
    print_info(f"실행 중: {description}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_security_issues():
    """보안 문제 체크"""
    print_header("보안 체크 수행 중...")
    
    issues = []
    app_dir = Path("app")
    
    # 1. 하드코딩된 비밀번호 검사
    print_info("하드코딩된 비밀번호 검사 중...")
    password_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'PASSWORD\s*=\s*["\'][^"\']+["\']',
        r'password:\s*["\'][^"\']+["\']',
        r'vmcMrs75',
        r'akfh11',
    ]
    
    for py_file in app_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            for pattern in password_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        'file': str(py_file),
                        'line': line_num,
                        'type': '하드코딩된 비밀번호',
                        'content': match.group()
                    })
        except Exception as e:
            print_warning(f"파일 읽기 실패: {py_file} - {e}")
    
    # 2. CORS 설정 확인
    print_info("CORS 설정 확인 중...")
    init_file = app_dir / "__init__.py"
    if init_file.exists():
        content = init_file.read_text(encoding='utf-8')
        if 'origins: "*"' in content or "origins='*'" in content or 'origins="*"' in content:
            issues.append({
                'file': str(init_file),
                'line': 0,
                'type': 'CORS 모든 출처 허용',
                'content': 'CORS가 모든 출처(*)를 허용하고 있습니다.'
            })
    
    # 3. SECRET_KEY 기본값 확인
    print_info("SECRET_KEY 기본값 확인 중...")
    for py_file in app_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            # SECRET_KEY에 기본값이 있는지 확인 (단, warnings는 제외)
            # os.getenv('SECRET_KEY', 'default-value') 패턴만 찾기
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                # 주석이나 warnings는 제외
                if 'warnings' in line.lower() or line.strip().startswith('#'):
                    continue
                # SECRET_KEY = os.getenv('SECRET_KEY', 'default') 패턴 찾기
                if re.search(r"(SECRET_KEY|IG_BOARD_SECRET_KEY).*=.*os\.getenv\([^,)]+,\s*['\"][^'\"]+['\"]", line):
                    # 기본값이 빈 문자열이 아닌 경우만 문제로 간주
                    match = re.search(r"os\.getenv\([^,)]+,\s*['\"]([^'\"]+)['\"]", line)
                    if match and match.group(1) and match.group(1) not in ['', 'None']:
                        issues.append({
                            'file': str(py_file),
                            'line': i,
                            'type': 'SECRET_KEY 기본값 사용',
                            'content': f'SECRET_KEY에 기본값이 설정되어 있습니다: {match.group(1)[:20]}...'
                        })
        except Exception:
            pass
    
    # 4. 에러 메시지에서 민감한 정보 노출 확인
    print_info("에러 메시지 보안 확인 중...")
    for py_file in app_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            # traceback.format_exc()를 클라이언트에 반환하는지 확인
            if 'traceback.format_exc()' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if 'traceback.format_exc()' in line and 'jsonify' in line:
                        issues.append({
                            'file': str(py_file),
                            'line': i,
                            'type': '스택 트레이스 노출',
                            'content': '에러 응답에 스택 트레이스가 포함될 수 있습니다.'
                        })
        except Exception:
            pass
    
    # 결과 출력
    if issues:
        print_error(f"{len(issues)}개의 보안 문제가 발견되었습니다:")
        for issue in issues:
            print(f"  - {issue['file']}:{issue['line']} - {issue['type']}")
            print(f"    {issue['content']}")
        return False
    else:
        print_success("보안 체크 통과!")
        return True

def run_unit_tests():
    """유닛 테스트 실행"""
    print_header("유닛 테스트 실행 중...")
    
    # pytest 실행 (python3 사용)
    import shutil
    python_cmd = shutil.which("python3") or shutil.which("python") or "python3"
    success, stdout, stderr = run_command(
        f"{python_cmd} -m pytest tests/ -v --tb=short",
        "pytest 실행"
    )
    
    print(stdout)
    if stderr:
        print(stderr)
    
    if success:
        print_success("모든 테스트 통과!")
        return True
    else:
        print_error("테스트 실패!")
        return False

def check_dependencies():
    """의존성 보안 체크 (선택사항)"""
    print_header("의존성 보안 체크 중...")
    
    # safety가 설치되어 있으면 실행
    success, _, _ = run_command("which safety", "safety 설치 확인")
    if success:
        success, stdout, stderr = run_command(
            "safety check",
            "safety 보안 체크"
        )
        if stdout:
            print(stdout)
        if stderr and "No known security vulnerabilities" not in stderr:
            print_warning("의존성 취약점이 발견되었습니다:")
            print(stderr)
            return False
        else:
            print_success("의존성 보안 체크 통과!")
    else:
        print_warning("safety가 설치되지 않았습니다. 설치하려면: pip install safety")
    
    return True

def main():
    """메인 함수"""
    print_header("자동화된 테스트 및 보안 체크 시작")
    
    # 현재 디렉토리 확인
    if not Path("app").exists():
        print_error("app 디렉토리를 찾을 수 없습니다. 프로젝트 루트에서 실행해주세요.")
        sys.exit(1)
    
    results = {
        'tests': False,
        'security': False,
        'dependencies': True
    }
    
    # 1. 보안 체크
    results['security'] = check_security_issues()
    
    # 2. 유닛 테스트
    results['tests'] = run_unit_tests()
    
    # 3. 의존성 체크 (선택사항)
    results['dependencies'] = check_dependencies()
    
    # 최종 결과
    print_header("최종 결과")
    
    all_passed = all(results.values())
    
    if results['security']:
        print_success("보안 체크: 통과")
    else:
        print_error("보안 체크: 실패")
    
    if results['tests']:
        print_success("유닛 테스트: 통과")
    else:
        print_error("유닛 테스트: 실패")
    
    if results['dependencies']:
        print_success("의존성 체크: 통과")
    else:
        print_warning("의존성 체크: 경고")
    
    if all_passed:
        print_success("\n🎉 모든 체크 통과!")
        sys.exit(0)
    else:
        print_error("\n⚠️  일부 체크 실패. 위의 내용을 확인하고 수정해주세요.")
        sys.exit(1)

if __name__ == "__main__":
    main()

