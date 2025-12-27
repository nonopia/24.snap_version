# version.json 생성 도구

import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime
import os, io

VERSION_INFO_DIC = {
        "version": "",
        "release_date": "",
        "download_url": "",
        "checksum": "",
        "file_size": 0,
        "change_log": [],
        "force_update": False
    }
    
exe_file = "snap_crypt.exe"
version_json_file = "version.json"
download_main_url = "https://raw.githubusercontent.com/nonopia/24.snap_version/main/"
download_json_url = download_main_url + version_json_file
download_exe_file_url = download_main_url + exe_file


import PyInstaller.__main__ #python make_version_json.py --build
separator = ';' if os.name == 'nt' else ':' #Windows ';' / Linux ':' 
absolute_path_name = Path(sys.argv[0]).resolve()  # 절대 경로로 변환
script_dir = absolute_path_name.parent
filename_stem = absolute_path_name.stem  #ext 없는 finename
exe_filename = absolute_path_name.stem  ## 출력 파일 이름
if "--build" in sys.argv:
    build_dist_dir = script_dir / "build_dist"
    build_dist_dir.mkdir(exist_ok=True)
    PyInstaller.__main__.run([
        str(absolute_path_name),           # 전체 경로 (문자열로 변환)
        f'--name={exe_filename}',          # 출력 파일 이름
        '--onefile',
        '--noupx',
        '--noconsole',
        f'--icon={script_dir / "build_dist" / "_icon" / "locker_icon.ico"}',
        f'--distpath={build_dist_dir}',
        f'--workpath={build_dist_dir}',
        f'--specpath={build_dist_dir}'
#        f'--add-data={os.path.join(".", "remote_info.json")}{separator}.', # ./1.json이 실행시에는 _MEI/1.json에 위치
#        f'--add-data={os.path.join(".", "data", "remote_info.json")}{separator}config', #./data/1.json이 실행시에는 _MEI/config/1.json에 위치
#        '--hidden-import=pyscreeze', '--hidden-import=pillow', '--hidden-import=numpy',
#        '--exclude-module=pwd', '--exclude-module=grp', '--exclude-module=fcntl', '--exclude-module=termios', '--exclude-module=PyQt5'
    ])
    spec_file = build_dist_dir / f'{filename_stem}.spec'     # spec 파일 삭제
    spec_file.unlink(missing_ok=True)
    sys.exit(0)


def calculate_checksum(file_path: Path) -> str:
    """파일의 SHA256 체크섬 계산"""
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return f"sha256:{sha256_hash.hexdigest()}"

def create_version_json(version: str, download_url: str, exe_path: Path, change_log: list, output_path: Path = None, force_update: bool = False):
    """
    version.json 파일 생성
    Args:
        version: 버전 번호 (예: "1.1.0")
        download_url: 다운로드 URL
        exe_path: 실행 파일 경로
        change_log: 변경사항 목록
        output_path: 출력 파일 경로 (기본: version.json)
        force_update: 강제 업데이트 여부
    """
    if not exe_path.exists():
        print(f"오류: 파일을 찾을 수 없습니다 - {exe_path}")
        return False
    
    checksum = calculate_checksum(exe_path)
    file_size = exe_path.stat().st_size

    # version.json 데이터 생성
    VERSION_INFO_DIC.update({
        "version": version,
        "release_date": datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),
        "download_url": download_url,
        "checksum": checksum,
        "file_size": file_size,
        "change_log": change_log,
        "force_update": force_update
    })

    # 출력 경로 설정 및 JSON 파일 저장     
    if output_path is None:
        output_path = Path(version_json_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(VERSION_INFO_DIC, f, indent=2, ensure_ascii=False)
    
    print(f"\nversion.json 생성 완료: {output_path}")
    print("\n생성된 내용:")
    print("=" * 60)
    print(json.dumps(VERSION_INFO_DIC, indent=2, ensure_ascii=False))
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
    print()
    print("=" * 60)
    print("version.json 생성 도구")
    print("=" * 60)
    print()
    
    version = get_user_input(f"버전 번호(빈 줄시 : 1.1.0 로 기본 설정): ", "1.1.0")
    exe_path = get_user_input(f"실행 파일(빈 줄시 {exe_file} 로 기본 설정): ", exe_file, "file")
    download_url = get_user_input(f"다운로드 URL:(빈 줄시 {download_exe_file_url} 로 기본 설정): ", download_exe_file_url)
    force = get_user_input(f"강제 업데이트? (y/n, 빈 줄시 'n'로 기본 설정): ", "n").lower()

    print("변경사항을 입력하세요 (빈 줄 입력 시 종료):")
    change_log = []
    while True:
        item = input(f"  {len(change_log) + 1}. ").strip()
        if not item:
            break
        change_log.append(item)
    
    # version.json 생성
    create_version_json(
        version=version,
        download_url=download_url,
        exe_path=exe_path,
        change_log=change_log,
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
