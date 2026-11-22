# P3 v653 — 사용자 PC 테스트 ZIP 인계 / 로컬 패키징 검증 (2026-11-22)

**성격:** Windows Actions 공식 결과가 아닌, 기존 v647 검증 소스 ZIP의 정확한 v653 UI 파일만 교체해 만든 **ChatGPT 격리 Linux 컨테이너 오프라인 테스트 ZIP**. 실제 Windows PC SimC 검증 또는 신규 제품 완성을 주장하지 않는다.

## 원본·내용 정체성

- source branch: `probe/chat-cache-v035-20261024`.
- ZIP 제작 당시 확인한 개발 HEAD: `a4a77d19478270549115c6e41504779c1993fcf4` (v653 UI 확정본).
- 원본 v647 내부 ZIP: SHA256 `debb25affa7e0539f2197a267deb5286d566b57510cec1d3412e838b28edfdd2` (이전 Windows CI `#44677378569`, 이력이 현재 변경 CI를 대체하지 않음).
- 새 사용자 전달 파일: `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA_v653_PC_TEST.zip`, **1,513,394 bytes**, SHA256 `1afbc287a8600c1a07be1eb0f10d5c06347581b1b52fc56e3bdd27d72239c0c3`.
- 내부 원래 root `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA/`, 기존 실행 진입점 `START_HERE_AUTO_SETUP_AND_RUN.bat` 유지.
- 제품 파일 283개 + `V181_PACKAGE_MANIFEST.json` = 284 archive entries. 변화는 아래 UI **3개 파일만**이며, 그 외 280개 제품 파일의 bytes 및 패키징 entry metadata는 v647와 같다. 매니페스트의 3개 SHA256/size를 실제 새 바이트로 갱신하고 전체 283개 다시 검증함. 기존 manifest `runtime_identity_bytes_unchanged` true 유지. Windows 명령·SimC 원본 코드·Native 계산·서명 세션/캐시를 변경하지 않았다.
- 변경 UI 파일과 GitHub **Git blob SHA1** 직접 일치:
  - `runner/webui/index.html`: `75ea7c56a9ee7f70de2396a727ceca433f334523`.
  - `runner/webui/styles.css`: `47e3ed5b9dd7d704106d761e19a70c3d38e89766`.
  - `runner/webui/app.js`: `d98f4b26342db404d4587ce18f09752a27ff87c6`.

## 이번 턴에서 새로 실행해 통과한 검사

1. ZIP CRC `testzip` PASS, manifest 283/283 SHA256 + size PASS, root/path uniqueness PASS, 280 unchanged product bytes 직접 비교 PASS.
2. Extracted real `runner/webui/app.js`: `node --check` PASS.
3. Extracted `runner/webui/index.html`: 201 unique ids, `label[for]` 참조 모두 존재. 환경 1·2줄 순서 및 14개 표시 마법부여 슬롯 정합 PASS. 가슴/다리 2칸 배치 클래스 보존.
4. Extracted production JS의 실제 `eligibleEquipment` 함수 Node 실행: 설치 목록 정렬 캐시, 같은 목록 재사용, 배열/새 시즌 교체 시 갱신 PASS.
5. 실제 `syncOilUseToggle` 함수 Node 실행: 사용/미사용 dropdown와 기존 bool·표시 상태 동기화 PASS.
6. 압축 해제 Python 3.13 Linux FastAPI TestClient: `/`, `/assets/app.js`, `/assets/styles.css` 3개 경로 HTTP200 + nosniff/no-store, `/api/v1/health`, `/api/v1/defaults`, `/api/v1/options`, `/api/v1/sessions` 4개 인증된 로컬 GET HTTP200 PASS. `/health` 결과 DPS 지원 전문화 26, Native 미호출 확인.
7. 외부 Blizzard/WCL/Wago DB2/SimC Native 요청 **0회**.

**이번 ZIP에서 아직 실행하지 않은 검증:** Windows 3.12/3.14 공식 Actions 회귀 289+ 패키징 5, 실제 Windows Chrome/SimC binary 연결, 사용자 PC의 V229 최초 원본 오류·동시 cancel/resume/최종 DPS E2E. 이 ZIP을 **공식 Windows CI 통과 ZIP이나 모든 기능 PASS로 과장하지 않는다**. 기존 v647의 Windows CI, v639 Native64는 이력으로만 보존.

## 사용자에게 전달할 절차 및 미확정 사항

Windows PC에서 ZIP 다운로드 → 파일 자체를 마우스 우클릭해 모두 추출 → 루트 `SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA` 안의 `START_HERE_AUTO_SETUP_AND_RUN.bat` 실행 → 안내에 따라 필요한 Python/SimC 설정. 원본 ZIP 내부 바이너리·토큰·현재 사용자 장비/세션은 포함하지 않는다. Python 3.12+ 환경 필요; 사용자의 현재 Windows 정책/백신/SSL 등은 미검증.

테스트 순서: 앱 화면/새 v653 환경 구성(타깃·전투시간·소켓·기름 사용/미사용, 음식·영약·물약·증강 룬, 마법부여) → SimC 연결 확인 → 시즌 환경 구축 → 가능하면 최적화 → 저장된 결과 재열람. V229 실패 재발 시 **첫 실패 코드와 기존 ‘진단 영수증 복사’**만 수집하고 연쇄 PENDING을 개별 새 오류로 오인하지 않는다. 비밀키·실 PC 경로·프로필 원문을 공유할 필요 없음.

공식 `15/78 COMPLETE`, `full_product_e2e=PENDING`, `next_review=B10`. UI 버전은 v653 동결, v651/v652 rollback history 유지. GitHub main, v003, Project UI, Work OS, Shared State, 주 채팅 소유권 변경 없음.
