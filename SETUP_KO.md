# v033 GitHub Actions 초보자 설치 안내 (Windows 기준)

## 실행 환경과 무료·공개 범위

- **첫 설치는 GitHub 개인 계정의 비공개(Private) 저장소**가 기본 권장안입니다.
- GitHub Free 개인 계정의 비공개 저장소는 표준 GitHub 호스팅 러너 **월 2,000분**과 별도 저장소/캐시 한도를 사용합니다. 사용량을 초과하거나 저장소 설정이 다르면 비용/차단이 발생할 수 있으므로 계정 Billing 페이지에서 확인하세요.
- Public의 **표준** 호스팅 러너는 실행 시간 요금이 무료이지만 소스, 이 특성 코드, 설정, 작업 로그, Artifacts에 접근할 수 있는 범위가 넓어집니다. 프로젝트 전체를 공개할 의도가 없다면 추천하지 않습니다.
- 이 파일은 두 비교 케이스만 실행합니다. v032 전체 CHMV 최적화가 아닌 *Linux native 호환성 시험*입니다.

## 1. GitHub 저장소 만들기

1. https://github.com/ 로그인/계정 생성 (가능하면 2단계 인증 설정).
2. 오른쪽 상단 **+** 메뉴 → **New repository**.
3. **Repository name**을 `simc-secondary-optimizer-runner`로 설정합니다.
4. **Private**를 선택합니다. Organizations가 아닌 자신의 개인 계정으로 시작하는 것이 간단합니다.
5. **Add a README file** 체크 후 **Create repository**를 누릅니다.
6. 생성된 저장소 URL(예: `https://github.com/내계정/simc-secondary-optimizer-runner`)을 기록합니다. 비밀번호/토큰은 누구에게도 보내지 마세요.

## 2. 파일 업로드 (GitHub Desktop 추천)

1. https://desktop.github.com/ 에서 GitHub Desktop 설치, 로그인.
2. **File → Clone repository**에서 방금 만든 저장소를 선택하고, 원하는 `Local path`를 정해 **Clone**.
3. 본 v033 ZIP을 **별도 폴더**에 풀고, 그 안의 모든 항목을 복제한 저장소 로컬 폴더에 복사합니다. **ZIP 자체를 복사하는 게 아닙니다.**
4. 루트에 `README.md`, `SETUP_KO.md`, `runner`, `inputs`, `fixtures`, `tests`, `.github` 폴더가 보여야 합니다. `README.md` 기존 내용을 v033의 파일로 덮어씁니다.
5. 특히 **`.github/workflows/remote-simc-v033.yml`** 경로가 정확히 존재하는지 확인합니다.
6. GitHub Desktop에서 **Changes**에 파일들이 표시되면 Summary에 `Add v033 pinned SimC cloud pilot`을 입력하고 **Commit to main**.
7. **Push origin**. GitHub 웹 저장소에서 `.github/workflows/remote-simc-v033.yml` 파일이 보이는지 확인합니다.

**대안:** GitHub 웹에서 업로드할 수도 있지만, 여러 폴더와 `.github` 경로를 빠뜨리기 쉬워 Desktop을 권장합니다.

## 3. Actions 권한 확인

1. 저장소에서 **Actions** 탭.
2. 처음 사용 시 'I understand my workflows, go ahead and enable them' 같은 활성화 안내가 나타나면 내용을 확인하고 활성화.
3. 만약 목록에 보이지 않으면 **Settings → Actions → General**에서 Actions 허용 설정을 확인합니다.
4. **`v033 Pinned Linux SimC Compatibility Pilot`**가 보여야 합니다.
5. **주의:** 다른 자동화 workflow를 추가하거나 외부 Pull Request용 실행 권한을 넓힐 필요는 없습니다. 이 파일은 수동 실행만 지원합니다.

## 4. 실제 SimC 클라우드 시험

1. **Actions** → 왼쪽 **v033 Pinned Linux SimC Compatibility Pilot** 선택.
2. 오른쪽 **Run workflow** → Branch `main` 확인.
3. `rune`: **both**, `iterations`: **60** 선택 → **Run workflow**.
4. 표시되는 실행 항목을 열고 각 단계의 성공·실패를 확인합니다. 첫 실행에서 Linux SimC 소스를 다운로드하고 CLI를 빌드하므로 빌드와 컴파일 단계가 있습니다.
5. 완료 후 실행 요약 하단의 **Artifacts** 영역에서 `simc-v033-native-evidence-<번호>` 다운로드.
6. 받은 ZIP을 개발 채팅에 업로드합니다. **사용자 GitHub 로그인 정보, PAT, 비밀번호는 필요 없고 보내지 않습니다.**

## 5. 결과 해석

- `PASS_ALL_NATIVE`: 요청한 1~2개의 Linux 네이티브 JSON2가 조건을 충족했습니다. *전체 제품/최적값 보증은 아님*.
- `PARTIAL_OR_BLOCKED`: SimC가 출력했으나 룬/장비/CHMV 검증에 실패하거나 실행이 중단됐습니다. Artifact의 `RUN_RECEIPT_v033.json`, 각 `stderr.txt`, `stdout.txt`, `result.json`을 분석합니다.
- GitHub 작업이 **Build Linux CLI** 단계에서 실패: `cmake_build.log`, 단계의 로그를 공유합니다.
- **Fetch exact pinned upstream SimC source**에서 실패: `7bc1071`이 현 GitHub clone에서 checkout되지 않은 것입니다. `main`이나 최신 버전으로 **임의 대체하지 말고** 실패 로그와 함께 보고합니다.
- Run workflow 버튼이 없음: yml이 기본 브랜치에 올라갔는지, `.github/workflows/`가 올바른지, Actions가 켜졌는지 확인합니다.
- 사용량/과금이 걱정되면 저장소의 **Settings → Actions → General** 및 계정 **Billing and licensing**의 Actions 사용량과 예산 알림을 확인하세요. 월 2,000분은 보장된 무료 할당량이지 작업 성공·무제한 무료 보증은 아닙니다.

## 6. 이후 ChatGPT 연결

별도의 **GitHub 연결 기능**을 설치·승인해야 ChatGPT가 GitHub 저장소를 직접 조회할 수 있습니다. 연결만으로 임의의 Actions 실행 권한이 자동 부여되지는 않습니다. 지원되는 작업 실행/코드 변경은 사용자 권한 및 Work 모드/연결 기능에 따라 달라집니다. 최초에는 ZIP을 반환하는 방식으로 Linux 동등성부터 검증합니다.

**원칙:** 업로드/실행하는 GitHub 저장소는 제품 개발 시험 전용이며, 공식 Work OS M0 허가·상태/Shared State 변경이 아닙니다.
