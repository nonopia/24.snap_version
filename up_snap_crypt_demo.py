#!/usr/bin/env python3
# snap_crypt_demo.py
# 자동 업데이트 기능 데모 프로그램

import sys
from pathlib import Path

# auto_updater 모듈 import
try:
    from up_auto_updater import AutoUpdater
except ImportError:
    print("오류: auto_updater.py 파일이 필요합니다.")
    sys.exit(1)

# 프로그램 버전 정보
VERSION = "1.0.0"
PROGRAM_NAME = "snap_crypt"
UPDATE_URL = "https://raw.githubusercontent.com/username/snap_crypt/main/version.json"

def main():
    """메인 프로그램"""
    print("=" * 60)
    print(f"{PROGRAM_NAME} v{VERSION}")
    print("자동 업데이트 기능 데모")
    print("=" * 60)
    print()
    
    # 메뉴 표시
    while True:
        print("\n--- 메인 메뉴 ---")
        print("1. 업데이트 확인")
        print("2. 프로그램 정보")
        print("3. 종료")
        print()
        
        choice = input("선택 (1-3): ").strip()
        
        if choice == "1":
            check_and_update()
        elif choice == "2":
            show_info()
        elif choice == "3":
            print("\n프로그램을 종료합니다.")
            break
        else:
            print("\n잘못된 선택입니다.")

def check_and_update():
    """업데이트 확인 및 적용"""
    print("\n" + "=" * 60)
    print("업데이트 확인")
    print("=" * 60)
    print()
    
    # AutoUpdater 생성
    updater = AutoUpdater(
        current_version=VERSION,
        update_url=UPDATE_URL
    )
    
    # 업데이트 확인
    update_info = updater.check_for_updates()
    
    if not update_info:
        print("\n현재 최신 버전을 사용 중입니다.")
        input("\n엔터를 눌러 계속...")
        return
    
    # 업데이트 정보 표시
    print("\n새 버전이 발견되었습니다!")
    print("-" * 60)
    print(f"현재 버전: {VERSION}")
    print(f"최신 버전: {update_info['version']}")
    print(f"출시일: {update_info.get('release_date', 'Unknown')}")
    print(f"파일 크기: {update_info.get('file_size', 0) / 1024 / 1024:.2f} MB")
    print()
    print("변경사항:")
    for item in update_info.get('changelog', []):
        print(f"  • {item}")
    print("-" * 60)
    print()
    
    # 사용자 확인
    response = input("업데이트를 진행하시겠습니까? (y/n): ").strip().lower()
    
    if response != 'y':
        print("\n업데이트를 취소했습니다.")
        input("\n엔터를 눌러 계속...")
        return
    
    print()
    
    # 다운로드
    new_exe = updater.download_update(
        update_info['download_url'],
        update_info['checksum'],
        progress_callback=lambda p: print(f"\r진행률: {p}%", end='', flush=True)
    )
    
    print()  # 줄바꿈
    
    if not new_exe:
        print("\n업데이트 다운로드에 실패했습니다.")
        input("\n엔터를 눌러 계속...")
        return
    
    # 업데이트 적용
    print("\n업데이트를 적용합니다...")
    if updater.apply_update(new_exe):
        print("\n업데이트가 적용되었습니다.")
        print("프로그램이 재시작됩니다...")
        sys.exit(0)
    else:
        print("\n업데이트 적용에 실패했습니다.")
        input("\n엔터를 눌러 계속...")

def show_info():
    """프로그램 정보 표시"""
    print("\n" + "=" * 60)
    print("프로그램 정보")
    print("=" * 60)
    print()
    print(f"프로그램: {PROGRAM_NAME}")
    print(f"버전: {VERSION}")
    print(f"업데이트 서버: {UPDATE_URL}")
    print(f"실행 경로: {Path(sys.argv[0]).resolve()}")
    print()
    input("엔터를 눌러 계속...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n프로그램을 중단합니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        input("\n엔터를 눌러 종료...")
        sys.exit(1)
