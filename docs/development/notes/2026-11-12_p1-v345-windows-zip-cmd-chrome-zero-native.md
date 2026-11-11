# v345 — 소스 ZIP 실제 Windows CMD 설치 경로·Chrome 세션 저장/재열기

- **Capability:** `PRODUCT.E2E`, `DEV.CONTINUITY`.
- **Keywords:** P1, v345, Windows ZIP, extracted application, CMD, localhost, Chrome, saved session, restart, v181, v344, no DPS Native.
- **Prior evidence:** [v344 GitHub Windows Chrome→70783 Native64 PASS](2026-11-12_p1-v344-real-windows-browser-native64-once.md), [v181 Windows 배포 ZIP·HTTP PASS](../../V181_P1D_WINDOWS_LOCAL_BETA_PACKAGE_REAL_HTTP_20261030.md), v181 원본 패키징 workflow.
- **Decision:** `CONNECT` — v344에서 이미 현재 시즌 Windows 사용자 기본 N56/64와 결과 복원 실 Native PASS를 확보했으므로, 또 다른 64회를 무조건 계산하지 않는다. 기존 v181 source-only ZIP packager, 진짜 압축 해제 `.cmd` 실행기, 브라우저, 원본 `/sessions/plan` Native0, 저장·서버 재기동·최근 세션 목록 복원만 확인. 실행파일과 원본 캐시/세션은 ZIP에 섞지 않는다.
- **Changes:** `p1_v345_windows_extracted_zip_cmd_browser_restore.py`, `p1_v345_windows_extracted_zip_cmd_browser_once.yml`, Windows 시작 문서 최신 제품 문구 명시(오래된 6회 기록과 64회 기본 구별). 검증된 역사 v213 소스 아티팩트를 기존 경로로 가져오되 현 70783 원본 인증으로 과장하지 않는다. 기존 `v181_windows_beta_packager.py`의 명시 파일 허용 목록과 SHA/ZIP 보호를 유지. 정확 공식 Windows `de11f57` 바이너리는 ZIP **외부**에서 배너만 확인하고 현재 제품 소스와 별도 identity 처리.
- **Verification:** One-shot Actions `[v345-win-package-once]` 영수증 확인 전 **PENDING**. 검사는 ① source artifact/SHA ② deterministic ZIP/원본 SHA ③ `--check` Native0 ④ 진짜 압축 해제 CMD→127.0.0.1:8765 ⑤ 실제 Chrome 26 DPS 초기화와 공식 SimC 경로 입력 ⑥ 사용자 입력 기반 plan Native0→로컬 세션 보존 ⑦ CMD/Python 종료→같은 ZIP CMD 재시작→Chrome 목록에서 저장된 세션 직접 클릭 복원을 순서대로 확인한다. 해당 세션은 **계획만 수립한 세션**이므로 완료된 DPS 결과 재열기 실증은 v344 원본을 재사용하며 v345가 독립적으로 결과를 생성한 척하지 않는다.
- **Remaining:** 개인 PC 실사용/브라우저 설정/관리형 SimC 자동 설치 UX, 최초 70783 시즌 구축의 개인 API 자격증명 없이 동작 여부, 새 시즌 G/J/F/O, 다양한 아이템·특성·26 전문화 전체 Native는 여전히 별도 검증·제품 개선 범위. 역사 v213 카탈로그를 최신 70783 새 시즌 승인으로 취급하지 않는다.
- **Efficiency:** 신규 DPS Native0 / 환경 Native0, v344 원본 64 증거 그대로 재사용. 배포 아카이브 원본 SHA/허용 목록 검사, 소스 파일 byte-match, 사용자 세션 경로는 ZIP 밖. Windows v181 리그레션을 재사용하고 별도 native 시뮬레이터/엔진/전수 Gate는 추가하지 않는다.
