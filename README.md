snap_version control 디렉토리입니다.
시험용으로 사용될거예요.

# snap_crypt 자동 업데이트 시스템

snap_crypt의 자동 업데이트 기능 구현 예제입니다.

## 📁 파일 구성

```
auto_update_system/
├── auto_updater.py              # 자동 업데이트 모듈 (핵심)
├── snap_crypt_demo.py           # 데모 프로그램
├── create_version_json.py       # version.json 생성 도구
├── version.json                 # 버전 정보 파일 (샘플)
└── README.md                    # 이 파일
```

## 🚀 빠른 시작

### 1. 필수 라이브러리 설치

```bash
pip install requests packaging
```

### 2. 데모 프로그램 실행

```bash
python snap_crypt_demo.py
```

## 📖 사용 방법

### A. 프로그램에 자동 업데이트 기능 추가

```python
from auto_updater import AutoUpdater

# 프로그램 버전 정의
VERSION = "1.0.0"
UPDATE_URL = "https://your-server.com/version.json"

# AutoUpdater 생성
updater = AutoUpdater(
    current_version=VERSION,
    update_url=UPDATE_URL
)

# 업데이트 확인
update_info = updater.check_for_updates()

if update_info:
    # 새 버전이 있음
    print(f"새 버전: {update_info['version']}")
    
    # 다운로드
    new_exe = updater.download_update(
        update_info['download_url'],
        update_info['checksum']
    )
    
    if new_exe:
        # 업데이트 적용 (프로그램 재시작)
        updater.apply_update(new_exe)
```

### B. version.json 생성

#### 방법 1: 도구 사용

```bash
python create_version_json.py
```

대화형으로 입력:
- 버전 번호
- 실행 파일 경로
- 다운로드 URL
- 변경사항

#### 방법 2: 수동 작성

```json
{
  "version": "1.1.0",
  "release_date": "2024-12-22",
  "download_url": "https://github.com/user/repo/releases/download/v1.1.0/snap_crypt.exe",
  "checksum": "sha256:abc123...",
  "file_size": 41943040,
  "changelog": [
    "새 기능: 다중 모니터 지원",
    "버그 수정: 메모리 누수 해결"
  ],
  "force_update": false
}
```

체크섬 계산:
```bash
# Windows
certutil -hashfile snap_crypt.exe SHA256

# Linux/Mac
sha256sum snap_crypt.exe
```

### C. 서버 배포

#### GitHub Releases 사용 (권장)

1. **Release 생성**
   - GitHub Repository → Releases → Create a new release
   - Tag: `v1.1.0`
   - Title: `snap_crypt v1.1.0`

2. **파일 업로드**
   - `snap_crypt.exe` 업로드

3. **version.json 배포**
   - `version.json` 파일을 main 브랜치에 커밋
   - Raw URL 사용: `https://raw.githubusercontent.com/user/repo/main/version.json`

#### 자체 웹 서버 사용

nginx 설정 예제:
```nginx
server {
    listen 443 ssl;
    server_name updates.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /updates/ {
        root /var/www/snap_crypt;
        add_header Access-Control-Allow-Origin *;
    }
}
```

파일 구조:
```
/var/www/snap_crypt/updates/
├── version.json
└── releases/
    └── v1.1.0/
        └── snap_crypt.exe
```

## 🔧 API 레퍼런스

### AutoUpdater 클래스

#### `__init__(current_version, update_url)`
- `current_version`: 현재 프로그램 버전 (예: "1.0.0")
- `update_url`: version.json URL

#### `check_for_updates() -> dict | None`
서버에서 최신 버전 확인

**반환값:**
- 새 버전이 있으면: version.json 데이터 (dict)
- 최신 버전 사용 중: None
- 오류 발생: None

#### `download_update(download_url, checksum, progress_callback=None) -> Path | None`
업데이트 파일 다운로드 및 검증

**매개변수:**
- `download_url`: 다운로드 URL
- `checksum`: SHA256 체크섬 (형식: "sha256:..." 또는 해시값)
- `progress_callback`: 진행률 콜백 함수 (0-100)

**반환값:**
- 성공: 다운로드된 파일 경로 (Path)
- 실패: None

#### `apply_update(new_exe_path) -> bool`
업데이트 적용 (파일 교체 및 재시작)

**매개변수:**
- `new_exe_path`: 새 실행 파일 경로

**반환값:**
- True: 성공 (프로그램 종료 후 재시작)
- False: 실패

#### `verify_checksum(file_path, expected_checksum) -> bool`
파일 체크섬 검증

**매개변수:**
- `file_path`: 파일 경로
- `expected_checksum`: 예상 체크섬

**반환값:**
- True: 일치
- False: 불일치

### 헬퍼 함수

#### `generate_version_json(version, download_url, exe_path, changelog) -> dict`
version.json 데이터 생성

**매개변수:**
- `version`: 버전 번호
- `download_url`: 다운로드 URL
- `exe_path`: 실행 파일 경로 (체크섬 계산용)
- `changelog`: 변경사항 목록

**반환값:**
- version.json 데이터 (dict)

## 🔐 보안 고려사항

### 필수 보안 요소

1. **HTTPS 사용**
   - 모든 통신은 HTTPS로만 수행
   - HTTP는 절대 사용 금지

2. **체크섬 검증**
   - 다운로드된 파일의 SHA256 체크섬 필수 검증
   - 체크섬 불일치 시 업데이트 중단

3. **백업 생성**
   - 업데이트 전 현재 실행 파일 백업
   - 실패 시 자동 복원

4. **타임아웃 설정**
   - 네트워크 요청: 10초
   - 다운로드: 300초 (5분)

### 권장 사항

- **디지털 서명**: Authenticode로 실행 파일 서명
- **버전 롤백 방지**: min_version 필드 사용
- **로깅**: 모든 업데이트 과정 로그 기록

## 🧪 테스트

### 테스트 시나리오

1. **정상 업데이트**
   ```bash
   # 1.0.0 → 1.1.0 업데이트 테스트
   python snap_crypt_demo.py
   ```

2. **네트워크 오류 시뮬레이션**
   ```python
   # 잘못된 URL로 테스트
   updater = AutoUpdater("1.0.0", "https://invalid-url.com/version.json")
   ```

3. **체크섬 불일치 테스트**
   ```python
   # 잘못된 체크섬으로 테스트
   updater.download_update(url, "sha256:wrong_checksum")
   ```

4. **백업 복원 테스트**
   - 업데이트 중 강제 종료
   - 배치 스크립트의 복원 로직 확인

## 📝 배포 워크플로우

### 1. 개발 완료
- 버전 번호 업데이트 (코드 내 VERSION 변수)
- 변경사항 문서화

### 2. 빌드
```bash
# PyInstaller로 실행 파일 생성
pyinstaller --onefile --noconsole snap_crypt.py
```

### 3. 체크섬 생성
```bash
# Windows
certutil -hashfile dist/snap_crypt.exe SHA256

# Linux/Mac
sha256sum dist/snap_crypt.exe
```

### 4. version.json 생성
```bash
python create_version_json.py
```

### 5. 서버 배포
- GitHub Release 생성 또는
- 웹 서버에 업로드

### 6. 테스트
- 이전 버전으로 업데이트 테스트
- 체크섬 검증 확인
- 백업/복원 시나리오 테스트

## 🐛 문제 해결

### 업데이트가 감지되지 않음
- version.json URL 확인
- 네트워크 연결 상태 확인
- 버전 번호 형식 확인 (MAJOR.MINOR.PATCH)

### 다운로드 실패
- 다운로드 URL 유효성 확인
- 파일이 서버에 존재하는지 확인
- 방화벽/프록시 설정 확인

### 체크섬 불일치
- version.json의 체크섬이 정확한지 확인
- 파일이 손상되지 않았는지 확인
- 다시 다운로드 시도

### 업데이트 후 실행 안됨
- 백업 파일(.exe.backup)로 수동 복원
- 로그 파일 확인
- 관리자 권한으로 실행

## 📚 추가 자료

- [시맨틱 버저닝](https://semver.org/lang/ko/)
- [GitHub Releases 문서](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [PyInstaller 문서](https://pyinstaller.org/)

## 📄 라이선스

이 코드는 예제용으로 제공됩니다. 프로젝트에 맞게 수정하여 사용하세요.

## 🤝 기여

버그 리포트나 개선 제안은 환영합니다!
