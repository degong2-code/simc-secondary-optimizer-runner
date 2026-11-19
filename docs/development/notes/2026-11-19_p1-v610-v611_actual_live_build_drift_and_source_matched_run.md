# P1 v610→v611 — 실제 현재 게임 빌드 drift와 동일 빌드 SimC 기반 영구마부 등록 시험

## P1 최종 목적

사용자 흐름: DPS 26전문화·목표 ilvl(기본 334) 또는 수동 최종 T → 시즌별 **G/J/F/O 전체 자동 계산**, B=G+J+F, T=B+O → 선택 영구마부 exact ID/실제 부위/정적 E(0 가능, 양수는 정확 수치) → 내부 대표 SimC 프로필 → 기존 적응형 DPS·SEM·95% 판정·근접 대안·캐시·취소/재개. 이번 단계는 실제 원본으로 v607/v608의 `product_input` 및 `chmv_budget` 네 Policy A 증거를 얻는 데 초점을 둔다. 새 효과 인증/엔진·전수 Native·장비 추천을 하지 않는다.

## v610 첫 실환경 실행 (완료·비용 최소)

- 실제 Win2022 [Actions #44425195290](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44425195290), 최종 **failure** (보안/정합 차단에 따른 예상된 테스트 신호). 압축 영수증 artifact **14482754801**, `V610_REAL_ENCHANT_ADMISSION_ONE_BUILD.json` 실제 다운로드 및 확인.
- 실제 KR 현재 게임 빌드: **12.1.5.70961** (live source SHA `ed80a261f9a1b91c4480fedb812ea1ec714ef6ed7c6ff14524ae61736ec7dff5`). 기존 재사용 가능한 검증 SimC 바이너리/원본: **12.1.5.70783**, 원본 commit `de11f57df75dda668bae6ac7043a43b98831fa96`; source/binary mismatch.
- 결과 **`PENDING_MATCHED_CURRENT_GAME_BUILD_SIMC`**, 최초 차단 `LIVE_BUILD_DIFFERS_FROM_70783_PINNED_BINARY`. **현재 게임 빌드 확인용 HTTP 조회는 수행; 시즌 Wago/DB2 테이블 수집 0, G/J/F/O Native 0, 사용자 DPS Native 0, 새 자동 승인 건수는 미측정**. 기존 70783 수치와 선택지를 새 70961의 유효 값으로 복사하지 않고 중단한 것은 올바른 정책 동작.
- 코드는 `integration_probes/p1_v610_real_installed_enchant_one_build.py`와 `.github/workflows/p1_v610_real_original_enchant_admission_once.yml`. 실제 빌드 일치 시에만 원래 `v113.LocalJobs.discover_season_myth_target` 및 `build_season_environment`(v216/v217/v212)를 호출한다. 결과는 검증된 per-item 네 receipt, 실제 등록 ID/정적 E, 첫 미확정 소유자와 기존 Native 호출 수만 bounded 기록한다. 소스/개인정보/비밀번호를 업로드하지 않는다.

## v611 최신 동일 빌드 SimC 확보

- 공식 `simulationcraft/simc` midnight HEAD **`9933ffb946fb55b1fa66657b848f519ac19006e1`**, commit 메시지는 **[live] Game data update (Build 70961)**. 해당 정확 커밋의 공식 GitHub [CI #44328474174](https://github.com/simulationcraft/simc/actions/runs/44328474174) Windows VS x64 **build SUCCESS**였으나 당해 run의 재사용 가능한 빌드 artifact는 없음. 기존 simc-publish 보존 artifact는 70783이라 최신 실행 파일이라고 사용할 수 없다.
- `integration_probes/p1_v611_current_live_70961_enchant_registration_once.py`는 기존 v610의 동일 정식 프로그램 source/Policy A/설치 진단을 **재사용**하고 새 빌드/SimC revision만 명확하게 변경한다. 실행 파일은 검증한 동일 git checkout에서 *현재 1회 컴파일*하며, **사전 공개된 SHA라고 과장하지 않고 실행에서 관측한 SHA + 원본 commit + SimC CLI 게임 banner를 묶어 보고**한다.
- `.github/workflows/p1_v611_current_live_70961_enchant_build_once.yml`은 해당 commit만 체크아웃, upstream과 동일한 MSVC+Ninja의 `BUILD_GUI=OFF` CLI 컴파일, 소스 SHA/Banner 검증, 저장소의 역사 시즌 JSON 격리 → 기존 정상 `v113→v216→v212` 1회 시작. 이전 빌드 원본·G/J/F/O 복사 금지. 필요한 경우에만 원래 환경 구축의 적은 Native G/J/F, 사용자 DPS는 등록 확인 전 0회.
- 실제 GitHub [Actions #44425813732](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44425813732)는 **실행 중**(이 글 작성 시점). 완료 전 승인 개수·성공 여부를 주장하지 않음.

## 성공/보류/다음 조건

1. 70961 실제 M1/M2 설치 성공 및 실제 `v212.published_verified_options` 건수를 확인. 없으면 product_input(E0)/정확 부위/원본 Wago quality receipt 중 **첫 누락 이유만** 보고하고 수정.
2. 등록 ID가 있어도 사용자의 실제 대표 장비 최종 ItemID 적용과 SimC DPS/SEM/95%까지 실행하기 전에는 `full_product_e2e=PENDING` 유지. 향후 실행은 **기존 적응형 Runner**와 같은 시즌 원본을 재사용하고 실제 변경된 범위에서만 제한된 Native 사용.
3. 단지 버전 drift 때문에 마부 효과 인증 Gate 추가·전체 26 DPS 반복·현재 시즌 정적 캐시 폐기·권한 변환 금지.

**권한:** 격리 브랜치만, main·immutable v003·원본 v016·Project UI·Work OS/Shared State·현재 주 제품 개발 채팅의 코드/Native 소유권 변경 없음. 공식 15/78 COMPLETE, full_product_e2e=PENDING.
