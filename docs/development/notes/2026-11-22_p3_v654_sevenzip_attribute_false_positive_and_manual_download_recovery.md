# P3 v654 — 실제 PC .7z 설치 오탐 수정 및 인증서 실패 시 수동 회복 (2026-11-22)

**기준:** 사용자 제공 v653 Windows 테스트에서 UI PASS, SimC update 공식 HTTPS CA 검증 실패, GitHub artifact 상세 링크 404, 직접 받은 0d19401 공식 Windows x64 archive의 `ARCHIVE_LINK_OR_ENCRYPTION_REFUSED` 설치 거부 확인. 사용자 승인 후 **기존 격리 브랜치**에서 업데이트/설치 코드만 변경. v653 디자인/CSS, Native DPS, 예산, v229 stage, 세션/캐시 원본 불변.

## 원인·개선

1. `runner/v193_simc_local_updater.py::verify_inventory`의 기존 `"l" not in attrs.lower() and "r" not in attrs.lower()`는 Windows 읽기 전용 `R`, POSIX `-rw-r--r--`까지 링크로 오인하여 거부. **원인은 코드 기준 확정**, 사용자 실물 7z의 정확한 속성 한 줄은 아직 미수집.
2. 정상 Windows `A/R/D/RA/....A`와 정상 POSIX `-rw-r--r--`, `drwxr-xr-x` 허용. 7z `Attributes`의 전체 표기 형식을 구분하며 Windows `L` reparse/link 및 POSIX `l` symlink/기타 장치·파이프 타입 차단. `Symbolic Link`/`Hard Link` 목표가 존재하면 거부. `Encrypted=+`는 별도 `ARCHIVE_ENCRYPTION_REFUSED`, 알 수 없는 속성은 `ARCHIVE_ATTRIBUTES_UNRECOGNIZED` fail-closed. Path traversal/중복/크기/폭탄, 추출 후 link/path 검사, PE64 검증, 실제 `simc.exe display_build=2` 및 포인터 원자적 교체 계약은 수정하지 않음. 실패 시 기존 active 바이너리 보존.
3. SimC GitHub fallback은 `/actions/runs/{id}/artifacts/{id}` 상세 URL 대신 **존재하는 `/actions/runs/{id}` 실행 기록 페이지**를 사용. GitHub 로그인 후 해당 실행의 `Artifacts`에서 `simc-nightly-win64-midnight` 선택하도록 안내. API상 unexpired Windows x64 artifact라도 실제 GitHub 다운로드 인증·현재 KR Live build 동일함을 과장하지 않음. 전체 workflow failed라도 Windows x64 작업이 성공할 수 있으므로 단순 결론으로 사용 가능 여부 추정 금지. **API 외부 자동 바이너리 다운로드 없음.**
4. 로컬 `.7z` 설치 메시지는 `7z.exe` 자동 탐색 위치(Windows PATH 또는 Program Files/Program Files (x86) 아래 7-Zip)와 **.7z 다운로드 파일 저장 위치 자유**를 구분. 수동 압축 해제 후 기존 `SimC 실행파일 경로` + `Git revision` 및 `SimC 연결 확인·저장`으로 진행하는 독립 fallback을 안내. 사용자가 직접 내려받은 원본의 배포 서명을 독립 확인하지 못한다는 경고 유지.
5. `runner/webui/app.js`에서 실제 설치 차단 코드별 설명 제공. TLS 미검증 우회 금지. `0d19401` 바이너리를 최신 70961 Live source와 같다고 표시하지 않으며 현재 KR 빌드 READY도 자동 승격하지 않는다.
6. `tests/test_v193_simc_local_updater.py`의 기존 테스트를 유지하고, R/POSIX 정상 속성 허용·Windows L/Unix l·하드링크·암호화·미인식 속성 차단 및 UI run link/수동 설치 설명 회귀를 추가.

## 이번 턴 신규 실행 검증과 정확한 한계

- v653 Windows PC 테스트 ZIP `1afbc287a8600c1a07be1eb0f10d5c06347581b1b52fc56e3bdd27d72239c0c3`을 기준으로 **수정된 제품 파일 3개**(`runner/v193_simc_local_updater.py`, `runner/webui/app.js`, `runner/webui/index.html`)를 정확한 격리 Git blob SHA와 바이트 대조했다.
  - v193: `2f4296461adf55c92b585aafdb809bbd305b190a`.
  - app.js: `51148aa398fea1142dba16bccf605f3c0e805e3a`.
  - index.html: `d78907fef5677476e749c6cbe78d051daae7fe32`.
  - 승인 v653 `runner/webui/styles.css` Git blob `47e3ed5b9dd7d704106d761e19a70c3d38e89766` **불변**.
- 독립 Linux 오프라인 focused 테스트 5 PASS(정상 읽기전용/Unix 권한, 실제 링크·암호화 차단, 경로 안전, GitHub 메타데이터 안전, 기존 CSS/수동 UI 연결), 진짜 production `checkSimcUpdater` JS mock-response 기능 검사 PASS, `node --check` PASS, `python -m py_compile` PASS.
- 압축 해제한 `v113` 로컬 FastAPI TestClient static 3 + API 5 = **8/8 HTTP200**, 외부 인증/SimC 호출 0.
- 새 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA_v654_PC_TEST.zip` **1,514,266 bytes**, SHA256 **`f59ccfdb8afe7cbc7500297f532192f3ce8fafe7432a79b63cdcedc677fbfeb5`**. 원래 283 제품파일 + manifest 1(archive 284 entries), 283/283 SHA256·size 및 ZIP CRC PASS. **변경 제품 파일 3개, v653 대비 불변 제품파일 280개**, 기존 루트 구조·`START_HERE_AUTO_SETUP_AND_RUN.bat` 보존. GitHub에 바이너리 ZIP을 업로드하거나 공식 Actions artifact로 기록하지 않았다. 사용자가 받은 파일 바이트는 사용자 채팅에만 전달.
- **미실행:** 신규 Windows Python3.12/3.14 전체 CI, 실제 Windows 7-Zip official `0d19401` archive 압축해제/PE64/DLL·실 SimC CLI, 신규 Native DPS/시즌 API/DB2, 사용자 PC v229 최초 오류 재검증. 오프라인 모의·정적/실 localhost 증거를 Windows Native PASS로 표기 금지.

## 사용자 재시험

- v654 새 ZIP을 **별도 폴더로 모두 추출**, 기존 사용자 세션/바이너리/캐시를 수동 삭제하거나 기존 7zip 실행 파일을 이동할 필요 없음.
- 이미 다운로드한 공식 `.7z`를 `내 PC의 .7z 파일 설치`에 연결하여 재시험. 최초 설치 중 새 코드 `ARCHIVE_ATTRIBUTES_UNRECOGNIZED`/LINK/ENCRYPTION/CLI 기동 오류가 재발한다면 코드 원문과 (개인경로·키 제외) 진단만 전달.
- 정상 설치 및 UI 반영 후 `SimC 연결 확인·저장`; `0d19401` 70783 생성 소스는 검증된 70961 Live 목표 소스보다 구버전이므로 동일 게임 빌드 READY 보장하지 않음. 사용자가 설치한 경로가 아닌 **이전 사용자 설정**은 별개로 유지.
- 공식 `15/78 COMPLETE` / `full_product_e2e=PENDING` / `next_review=B10` 고정. 격리 branch만 수정, main/v003 immutable/Project UI/Work OS/Shared State/주 개발 채팅 소유권 불변.

## 롤백

- 변경 전 정본 HEAD `cc10608a237a703213219b25d306e47cb2d362d9`에서 다음 **3개**만 복원 가능:
`git restore --source=cc10608a237a703213219b25d306e47cb2d362d9 -- runner/v193_simc_local_updater.py runner/webui/app.js runner/webui/index.html`; 변경 내역 검토 후 격리 branch에 별도 commit. CSS·세션·DPS/Native 캐시 원복 필요 없음. git reset --hard 금지.
