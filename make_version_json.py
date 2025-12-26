# version.json 생성 도구

import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime

exe_default_file_name = "snap_crypt.exe"
download_url_name = "https://raw.githubusercontent.com/nonopia/24.snap_version/main/version.json"
version_jason_file = "version.json"

def calculate_checksum(file_path: Path) -> str:
    """파일의 SHA256 체크섬 계산"""
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return f"sha256:{sha256_hash.hexdigest()}"

def create_version_json(version: str, download_url: str, exe_path: Path, changelog: list, output_path: Path = None, force_update: bool = False):
    """
    version.json 파일 생성
    Args:
        version: 버전 번호 (예: "1.1.0")
        download_url: 다운로드 URL
        exe_path: 실행 파일 경로
        changelog: 변경사항 목록
        output_path: 출력 파일 경로 (기본: version.json)
        force_update: 강제 업데이트 여부
    """
    if not exe_path.exists():
        print(f"오류: 파일을 찾을 수 없습니다 - {exe_path}")
        return False
    
    checksum = calculate_checksum(exe_path)
    file_size = exe_path.stat().st_size 

    # version.json 데이터 생성
    version_data = {
        "version": version,
        "release_date": datetime.now().strftime("%Y-%m-%d"),
        "download_url": download_url,
        "checksum": checksum,
        "file_size": file_size,
        "changelog": changelog,
        "force_update": force_update
    }
    
    # 출력 경로 설정 및 JSON 파일 저장     
    if output_path is None:
        output_path = Path(version_jason_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(version_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nversion.json 생성 완료: {output_path}")
    print("\n생성된 내용:")
    print("=" * 60)
    print(json.dumps(version_data, indent=2, ensure_ascii=False))
    print("=" * 60)    
    return True

def get_user_input(display_prompt: str, exe_default_file_name: str, file_option=""):
    '''
    "file" : 파일 경로를 찾아봄
    else : 단순 입력 조치
    '''
    while True:
        input_name = input(display_prompt).strip()
        if input_name == "":
            if file_option == "file":
                return_path = Path(exe_default_file_name)
            else:
                return_path = exe_default_file_name
        else:
            if file_option == "file":
                return_path = Path(input_name)
            else:
                return_path = input_name
        if file_option != "file":
            return return_path.strip()
        if not Path(return_path).exists():
            print("오류: 파일을 찾을 수 없습니다.")
            continue
        break
    return return_path

def main():
    print("=" * 60)
    print("version.json 생성 도구")
    print("=" * 60)
    print()
    
    version = get_user_input(f"버전 번호(빈 줄시 : 1.1.0 로 기본 설정): ", "1.1.0")
    exe_path = get_user_input(f"실행 파일(빈 줄시 snap_crypt.exe 로 기본 설정): ", exe_default_file_name, "file")
    download_url = get_user_input(f"다운로드 URL:(빈 줄시 {download_url_name} 로 기본 설정): ", download_url_name)
    force = get_user_input(f"강제 업데이트?(y/n, 빈 줄시 'n'로 기본 설정): ", "n").lower()

    print("변경사항을 입력하세요 (빈 줄 입력 시 종료):")
    changelog = []
    while True:
        item = input(f"  {len(changelog) + 1}. ").strip()
        if not item:
            break
        changelog.append(item)
    
    # version.json 생성
    create_version_json(
        version=version,
        download_url=download_url,
        exe_path=exe_path,
        changelog=changelog,
        force_update=force
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n중단되었습니다.")
    except Exception as e:
        print(f"\n오류: {e}")
        import traceback
        traceback.print_exc()
