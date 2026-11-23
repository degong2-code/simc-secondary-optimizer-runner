# P3 v670 — 동일 영약·보석 물리 ID의 복수 v212 설치본: 원본 영수증 차이 진단

2026-11-23 KST · 격리 브랜치 `probe/chat-cache-v035-20261024`
최종 코드·Windows 제품 HEAD: `941f41475e98c6db79253c5335f932a25c4f7861`

## 실제 사용자 PC 근거와 한계

- v669 제품 ZIP의 화염 마법사·ilvl334·기름 OFF·일반 4보석·SimC 관리형 CLI 12.1.5.70961 로컬 조회에서, 영약 F165·품질2가 조회되고 복수 설치본이 **동일 F/J와 동일 영약·보석 물리 ItemID**로 나타나 선택이 차단됨.
- 이는 `V216_UNQUALIFIED_MULTIPLE_INSTALLED_FJ_VARIANTS_SELECT_EXACT_SHA`의 실제 사용자 화면 재현. 동일 물리 ID라도 v212 설치 SHA의 입력·예산·원본·정책 옵션·SimC revision이 같다는 뜻은 아니므로 하나를 선택하거나 READY를 강제하지 않음.
- **실제 사용자 PC v212/v113 영수증 바이트는 GitHub에 없으며 이 변경에서 열람하지 못함.** 어떤 필드가 차이를 만든 것인지는 여전히 현장 진단 대기. 기존 70961 SimC CLI 연결은 현재 KR Live 빌드 인증이 아님.

## 최소 구현

- `runner/v113_local_web_api.py`: 기존 `LocalJobs.installed_oil_loadouts`의 **검증된** v212 exact SHA 및 저장 v113 일반 4보석/O=0 구성 범위에서만, 동일 물리 영약/품질/F/J/보석 ItemID 설치본의 원본 차이를 로컬에서 비교.
- 비교 항목: SimC revision, G 대표/무기 기준, B/T 회계, 각 G/J/F/O source identity, 영약 F Native 증거, O 벡터, source catalog, v216/v217 단계, trusted budget evidence, v222 회계, Policy A 옵션, DK 모듈, 보석 배치 원본. 비교용 각 그룹의 지문은 서버 내부에서만 계산하며 외부 응답에는 **차이가 발견된 범주 코드와 설치본 수**만 노출. 다른 범주에서 차이가 식별되지 않아도 `OTHER_SEALED_IDENTITY`로 남기며 절대 동등하다고 판정하지 않음.
- `runner/webui/index.html`·`app.js`: 기존 F/J 선택 차단 보존, `검증된 환경 구성` 아래 근거 차이 분류 및 **중복 원본 진단 복사** 버튼 표시. 클릭한 경우 같은 로컬 빌드/ilvl 조회 유효 범위에서만 `v670_local_verified_fj_collision_diagnostic_v1` JSON을 클립보드에 복사. 원본 SHA, 사용자의 경로, 프로필 본문, 비밀키를 복사하지 않음. 빌드 변경 시 이전 진단 소거.
- 신규 승인/랜덤 SHA·최신 설치본 선택·G/J/F/O 변형 병합 없음. 대체 프로필/장비 생성 없음. v212/v216/v217/기존 SimC adaptive·Native·95%·캐시·취소/재개/저장 수정 없음. 신규 DPS Native·시즌 DB2/HTTP 수집·SimC 컴파일 0.

## 테스트 및 패키지

- `tests/test_v669_verified_fj_physical_identity_offline.py`에 v670 합성 검증 설치본 비교(같은 물리 ID, 서로 다른 revision/J source), 원본 byte 보존, 불명확한 동일 범주 계속 보류, 실제 JS 진단 복사에서 SHA·경로 제외 및 빌드 변경 시 무효화 테스트 추가.
- 초기 CI에서는 신규 진단 UI가 최소 DOM 시험의 `getElementById` 부재를 처리하지 못했고, 추가 테스트의 JS 문자열 생성 오류도 있어 FAIL을 관측. 조건부 DOM 조회·JS fixture를 교정하여 최종 결과를 재확인. 과거 FAIL을 PASS로 바꾸어 기록하지 않음.
- 최종 Windows 패키지 [Actions #45102525780](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45102525780) **Win Python3.12/3.14 각각 349 PASS/0 FAIL**, 실제 압축해제·로컬 HTTP·기존 세션/계획 오프라인 PASS. [v113 API #45102525791](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45102525791) Ubuntu3.12/Windows3.14 각각 508 tests OK(skipped1). Focused/78 consistency 결과 분리 유지. 신규 Native 0.
- GitHub Actions wrapper artifact [#14786022690](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/45102525780/artifacts/14786022690)와 내부 제품 ZIP은 서로 다른 바이트. 사용자 전달 단일 `SIMC_SECONDARY_OPTIMIZER_v670_WINDOWS_BETA.zip`: **1,532,639 bytes**, SHA-256 `baca477142fd9886e0cbc425c6ba451c5a72b3c8db71cb9a1bd550fa0a07d316`. CRC PASS, package manifest 286/286 파일 SHA+size PASS, simc.exe 포함 없음, 로컬 개인 세션 포함 없음.

## 사용자 PC 최소 다음 작업 / STOP

1. 이전 CMD·localhost 탭을 정상 종료, 기존 설치와 세션 보존, 새 v670 ZIP을 별도 폴더에서 압축 해제 후 시작.
2. 기존 관리형 SimC 70961을 재사용; KR Live와 일치했다고 주장하지 않음. 기존 설치 목록 조회를 위한 수동 12.1.5.70961/ilvl334/O=0/4보석 구성 사용, 신규 시즌 G/F·Native 체크박스 OFF.
3. **시즌 환경 확인·설치, 선택 환경 검증·준비, DPS Native는 누르지 않음.** `2차 스탯 최적화`의 `검증된 환경 구성` 아래 `중복 원본 진단 복사`를 한 번 누르고 JSON만 공유. 비밀키·경로·전체 설치 파일 제출 불필요.
4. 진단으로 표시된 최초 차이 범주 하나가 실제 결과/프로필 적합성에 영향을 주는지 판단 후 **STOP→REUSE→최소 CONNECT/FIX**. 동등성에 필요한 증거가 부족하면 계속 차단; 자동 random SHA/수치 합치기 금지.

현재 개인 PC에서 해당 원본 차이 분야·정확 원인·시즌 READY·장신구2→Native DPS·SEM/95% E2E는 아직 미검증. 공식 `15/78 COMPLETE`(제품 구현률 아님), `full_product_e2e=PENDING`, `next_review=B10` 유지. main·v003 immutable·Project Sources UI·Work OS/Shared State·원본 v016 직접 통합·기존 주 개발 채팅 소유권은 변경하지 않음.
