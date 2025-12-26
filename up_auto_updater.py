# auto_updater.py
# snap_crypt 자동 업데이트 모듈

import requests
import json
import hashlib
import tempfile
import shutil
import sys
import subprocess
from pathlib import Path
from packaging import version as pkg_version

class AutoUpdater:
    """
    자동 업데이트 시스템
    
    GitHub Releases 또는 웹 서버에서 최신 버전을 확인하고
    자동으로 다운로드 및 설치하는 기능 제공
    """
    
    def __init__(self, current_version: str, update_url: str):
        """
        Args:
            current_version: 현재 버전 (예: "1.0.0")
            update_url: 버전 정보 JSON URL
        """
        self.current_version = current_version
        self.update_url = update_url
        self.exe_path = Path(sys.argv[0]).resolve()
        
    def check_for_updates(self) -> dict:
        """
        서버에서 최신 버전 정보 확인        
        Returns: dict: 업데이트 정보 (새 버전이 있을 경우) 또는 None
        """
        try:
            print(f"[업데이트] 버전 확인 중... ({self.update_url})")            
            response = requests.get(
                self.update_url,
                timeout=10,
                headers={'User-Agent': 'snap_crypt-updater'}
            )
            response.raise_for_status()
            
            remote_info = response.json()
            remote_version = remote_info.get("version")
            
            if not remote_version:
                print("[업데이트] 버전 정보 없음")
                return None
            
            print(f"[업데이트] 현재 버전: {self.current_version}")
            print(f"[업데이트] 최신 버전: {remote_version}")
            
            # 버전 비교
            if pkg_version.parse(remote_version) > pkg_version.parse(self.current_version):
                print(f"[업데이트] 새 버전 발견: {remote_version}")
                return remote_info
            else:
                print("[업데이트] 최신 버전 사용 중")
                return None
                
        except requests.exceptions.Timeout:
            print("[업데이트] 타임아웃 - 서버 응답 없음")
            return None
        except requests.exceptions.ConnectionError:
            print("[업데이트] 네트워크 연결 오류")
            return None
        except json.JSONDecodeError:
            print("[업데이트] JSON 파싱 오류")
            return None
        except Exception as e:
            print(f"[업데이트] 확인 실패: {e}")
            return None
    
    def download_update(self, download_url: str, expected_checksum: str, 
                       progress_callback=None) -> Path:
        """
        업데이트 파일 다운로드 및 무결성 검증
        
        Args:
            download_url: 다운로드 URL
            expected_checksum: 예상 SHA256 체크섬
            progress_callback: 진행률 콜백 함수 (0-100)
        
        Returns:
            Path: 다운로드된 파일 경로 또는 None
        """
        try:
            print(f"[업데이트] 다운로드 시작: {download_url}")
            
            # 임시 디렉토리에 다운로드
            temp_dir = Path(tempfile.mkdtemp())
            temp_file = temp_dir / "snap_crypt_update.exe"
            
            # 스트리밍 다운로드
            response = requests.get(
                download_url,
                stream=True,
                timeout=300,
                headers={'User-Agent': 'snap_crypt-updater'}
            )
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 8192
            
            print(f"[업데이트] 파일 크기: {total_size / 1024 / 1024:.2f} MB")
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 진행률 업데이트
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            if progress_callback:
                                progress_callback(progress)
                            
                            # 10% 단위로 출력
                            if downloaded % (total_size // 10) < chunk_size:
                                print(f"[업데이트] 다운로드 중... {progress}%")
            
            print("[업데이트] 다운로드 완료")
            
            # 체크섬 검증
            print("[업데이트] 무결성 검증 중...")
            if not self.verify_checksum(temp_file, expected_checksum):
                print("[업데이트] 체크섬 불일치 - 다운로드 파일 손상")
                temp_file.unlink()
                return None
            
            print("[업데이트] 무결성 검증 완료")
            return temp_file
            
        except requests.exceptions.Timeout:
            print("[업데이트] 다운로드 타임아웃")
            return None
        except requests.exceptions.ConnectionError:
            print("[업데이트] 다운로드 중 연결 끊김")
            return None
        except Exception as e:
            print(f"[업데이트] 다운로드 실패: {e}")
            return None
    
    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """
        파일의 SHA256 체크섬 검증
        
        Args:
            file_path: 검증할 파일 경로
            expected_checksum: 예상 체크섬 (형식: "sha256:..." 또는 해시값)
        
        Returns:
            bool: 검증 성공 여부
        """
        # "sha256:" 접두사 제거
        if expected_checksum.startswith("sha256:"):
            expected_checksum = expected_checksum[7:]
        
        # 파일 해시 계산
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        calculated_checksum = sha256_hash.hexdigest()
        
        print(f"[업데이트] 예상 체크섬: {expected_checksum[:16]}...")
        print(f"[업데이트] 계산 체크섬: {calculated_checksum[:16]}...")
        
        # 대소문자 무시 비교
        return calculated_checksum.lower() == expected_checksum.lower()
    
    def apply_update(self, new_exe_path: Path) -> bool:
        """
        다운로드된 파일로 현재 실행 파일 교체
        
        Args:
            new_exe_path: 새 실행 파일 경로
        
        Returns:
            bool: 성공 여부
        """
        try:
            print("[업데이트] 업데이트 적용 중...")
            
            # 현재 실행 파일 백업
            backup_path = self.exe_path.with_suffix(".exe.backup")
            
            if self.exe_path.exists():
                print(f"[업데이트] 백업 생성: {backup_path.name}")
                shutil.copy2(self.exe_path, backup_path)
            
            # 업데이트 스크립트 생성
            batch_script = self.create_update_script(new_exe_path, backup_path)
            
            print("[업데이트] 업데이트 스크립트 실행")
            print("[업데이트] 프로그램을 종료하고 재시작합니다...")
            
            # 배치 파일 실행 (백그라운드)
            if sys.platform == 'win32':
                subprocess.Popen(
                    [str(batch_script)],
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                subprocess.Popen([str(batch_script)], shell=True)
            
            # 프로그램 종료
            return True
            
        except Exception as e:
            print(f"[업데이트] 적용 실패: {e}")
            return False
    
    def create_update_script(self, new_exe: Path, backup: Path) -> Path:
        """
        업데이트 배치 스크립트 생성
        
        Args:
            new_exe: 새 실행 파일 경로
            backup: 백업 파일 경로
        
        Returns:
            Path: 배치 파일 경로
        """
        batch_path = self.exe_path.parent / "update_snap_crypt.bat"
        
        # Windows 배치 스크립트
        script_content = f"""@echo off
title snap_crypt 업데이트
echo ========================================
echo snap_crypt 자동 업데이트
echo ========================================
echo.
echo 업데이트를 진행합니다...
echo 잠시만 기다려주세요.
echo.

REM 프로세스 종료 대기 (5초)
timeout /t 5 /nobreak > nul

REM 파일 교체
echo 파일 교체 중...
move /Y "{new_exe}" "{self.exe_path}" > nul 2>&1

REM 교체 성공 여부 확인
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 업데이트 완료!
    echo ========================================
    echo.
    
    REM 백업 파일 삭제
    if exist "{backup}" (
        del "{backup}" > nul 2>&1
    )
    
    echo 프로그램을 다시 시작합니다...
    timeout /t 2 /nobreak > nul
    
    REM 프로그램 재시작
    start "" "{self.exe_path}"
) else (
    echo.
    echo ========================================
    echo 업데이트 실패!
    echo ========================================
    echo.
    echo 백업에서 복원 중...
    
    REM 백업에서 복원
    if exist "{backup}" (
        move /Y "{backup}" "{self.exe_path}" > nul 2>&1
        echo 복원 완료
    )
    
    echo 프로그램을 다시 시작합니다...
    timeout /t 2 /nobreak > nul
    
    REM 프로그램 재시작
    start "" "{self.exe_path}"
)

REM 임시 파일 정리
if exist "{new_exe.parent}" (
    rmdir /S /Q "{new_exe.parent}" > nul 2>&1
)

REM 배치 파일 자체 삭제
del "%~f0" > nul 2>&1
"""
        
        with open(batch_path, 'w', encoding='cp949') as f:
            f.write(script_content)
        
        return batch_path


def generate_version_json(version: str, download_url: str, 
                         exe_path: Path, changelog: list) -> dict:
    """
    version.json 파일 생성 헬퍼 함수
    
    Args:
        version: 버전 번호
        download_url: 다운로드 URL
        exe_path: 실행 파일 경로 (체크섬 계산용)
        changelog: 변경사항 목록
    
    Returns:
        dict: version.json 데이터
    """
    from datetime import datetime
    
    # 체크섬 계산
    sha256_hash = hashlib.sha256()
    with open(exe_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    
    checksum = f"sha256:{sha256_hash.hexdigest()}"
    file_size = exe_path.stat().st_size
    
    version_data = {
        "version": version,
        "release_date": datetime.now().strftime("%Y-%m-%d"),
        "download_url": download_url,
        "checksum": checksum,
        "file_size": file_size,
        "changelog": changelog,
        "force_update": False
    }
    
    return version_data


# 테스트용 메인 함수
if __name__ == "__main__":
    print("=" * 50)
    print("snap_crypt 자동 업데이트 모듈 테스트")
    print("=" * 50)
    print()
    
    # 테스트 설정
    updater = AutoUpdater(
        current_version="1.0.0",
        update_url="https://raw.githubusercontent.com/username/snap_crypt/main/version.json"
    )
    
    # 업데이트 확인
    update_info = updater.check_for_updates()
    
    if update_info:
        print()
        print("새 버전 발견!")
        print(f"버전: {update_info['version']}")
        print(f"출시일: {update_info['release_date']}")
        print(f"변경사항:")
        for item in update_info.get('changelog', []):
            print(f"  - {item}")
        print()
        
        # 사용자 확인
        response = input("업데이트를 진행하시겠습니까? (y/n): ")
        
        if response.lower() == 'y':
            # 다운로드
            new_exe = updater.download_update(
                update_info['download_url'],
                update_info['checksum']
            )
            
            if new_exe:
                # 업데이트 적용
                if updater.apply_update(new_exe):
                    print("[업데이트] 성공!")
                    sys.exit(0)
                else:
                    print("[업데이트] 적용 실패")
            else:
                print("[업데이트] 다운로드 실패")
    else:
        print()
        print("최신 버전을 사용 중입니다.")
