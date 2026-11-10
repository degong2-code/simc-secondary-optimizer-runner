# SIMC SECONDARY OPTIMIZER — P3-HAX 단일 최신 새 채팅 인계 (2026-11-10 KST)

**지위:** 본 문서가 최신 단일 진입점이며 기존 [P3-HAW](CHAT_CONTINUITY_HANDOFF_20261110_P3_HAW_OPTIMIZER_RESUME_ENGINE_FIRST.md)는 역사 인계로 보존한다. 본 인계는 제품 구현·공식 승격이 아니라 읽기 전용 복원과 다음 P2 연구의 연속성을 위한 것이다.

## 1. 실제 GitHub 기준과 권한

- 공개 저장소: `degong2-code/simc-secondary-optimizer-runner`
- 격리 작업 브랜치: `probe/chat-cache-v035-20261024`
- **이 인계 작성 직전 독립 조회 HEAD:** 격리 `e05780ca7e50601b813e6aaf3cbec716d0d282b8`; `main` `07133e0aaf738d6e4816a6486057b1cd49c018de`.
- GitHub compare 기준 격리 브랜치는 `main` 대비 **diverged / ahead 3288 / behind 7**. 병합·rebase·cherry-pick 금지. 격리 브랜치만 기존 권한 범위에서 사용한다. 본 인계 커밋으로 격리 HEAD는 이동하므로 새 채팅은 반드시 두 ref를 다시 독립 조회한다.
- HEAD 직전 최근 변경: `dbeaaf4c212d` v302 순수 지역 탐색 geometry/selector·회귀 테스트·실험 노트, `5f0331ec1302` 개발 노트 필수 heading 교정, `e05780ca7e50` P2 실험 최종 영수증 요약 및 인덱스 보충.
- 현재 HEAD의 Actions [#42757290762](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42757290762) SUCCESS: **556 tests = 554 PASS / 2 SKIP / 0 FAIL**, `DEV_LEDGER_PASS OFFLINE_NO_NATIVE_NO_NETWORK`. 이는 offline code/ledger 증거이며 신규 Native·웹 E2E 증거가 아니다.
- 우선순위: 최신 사용자 직접 결정·현재 Project 지침 > 승인 v1.4.1 및 2026-11-02 G/J/F/O 보충 v1.4.3 > 현재 코드/CURRENT/Actions/Native 영수증 > 역사 인계. GitHub 문서 커밋을 Project Sources/Instructions UI 적용으로 간주하지 않는다.

## 2. 최종 제품 목적과 승인된 불변 계약

**26개 DPS 전문화**에서 목표 ilvl(기본334) 또는 사용자가 지정한 **기름 포함 최종 CHMV 총량 T**를 기준으로 SimC DPS를 최대화하는 치명·가속·특화·유연의 **최적 절대 rating**을 찾는다. 관측 1순위, DPS/SEM, 95% 판정의 적용 범위, 실질적으로 다른 근접 대안, 비율, 정확 캐시·취소·재개를 제공한다. 관측 최고는 전역 최적 증명이 아니다.

- 사용자 입력: 직업·전문화·종족·특성, 목표 ilvl 또는 수동 최종 T, 장신구2, 선택 특수장비, 장식≤2, 보석·영약·음식·물약·기름·전투조건. 전체 착용 장비 입력/재분배, 장비 조합·획득 경로 추천, 시즌 전체 장비 DB는 제품 범위 밖.
- 제품은 대표 일반 장비·주능력치·무기·티어4·SimC 프로필을 내부 구성. 업로드 SimC는 캐릭터/특성 읽기용 선택 입력이며 현재 장비를 예산으로 복사하지 않는다.
- 공식 회계: `B=G+J+F`, `T=B+O`, `c_final=c_base+o`. 수동 최종 T 우선, O는 고정 비자유분배·한 번만 반영. 정확 특수장비 L은 G/B에 이미 포함되어 다시 더하지 않고 하한으로 보호. 정적 영구 마부 E도 중복 방지. 장신구 고정 스탯은 자유 G 밖. 제작장비 초기 50:50은 고정 하한 아님.
- 새 시즌은 G/J/F/O 전부 해당 시즌 원본·빌드·증거로 다시 결정하고 B/T 자동 갱신. 과거 시즌 79×2, J/F, oil 값을 새 시즌에 검증 없이 복사하지 않는다. exact Native G는 선택 경로이며 전 전문화·전 ilvl 전수 Gate가 아니다.
- 기본 보석은 **일반 치명·가속·특화·유연 각 1개(총4개)**. 특수보석은 필수 아님. 동일 효과/조건/범위가 증명된 최고 품질만 노출. 영구 마부는 지원, 일반 임시 마부는 제외, 무기 기름은 별도 O로 계속 지원.
- 효과·proc·APL·DPS는 SimC 책임. 독립 효과 인증 Gate나 효과 재구현 금지. 프로그램은 정확 ID/옵션·대표 프로필·GJFO/B/T·L/E/O 회계·정적 JSON2 rating 정합·후보 탐색·통계·캐시/취소/재개를 담당.
- 통계는 95%만 사용. 다중 후보를 보고 선택한 후 선택쌍의 근사 95%를 전역/가족단위 보증으로 확대하지 않는다.

**정책 자료:** [v1.4.1 DPS-only 교정본](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.1_DPS_ONLY_SCOPE_CORRECTION_20261031.md), [v1.4.3 시즌 G/J/F/O 승인 보충](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md), [Engine-first 실행 보충](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md). 현재 대화에 업로드된 v1.4.1 2026-10-29 파일과 GitHub의 2026-10-31 DPS-only 교정본은 파일명이 다르므로 동일 바이트라고 추정하지 않는다. Project UI 등록 여부는 별도 확인 전 미확인.

## 3. 반드시 읽을 자료와 순서

1. 본 P3-HAX 인계.
2. [제품 A~G 정본](PRODUCT_CANONICAL_STATUS_20261109_P3_HAI.md) 최상단 보충과 A~G 표.
3. [개발 프로토콜](development/PROTOCOL.md) → [START_HERE](development/START_HERE.md) → [기능 INDEX](development/INDEX.md) → [FILE_MAP](development/FILE_MAP.md) → [EVIDENCE_INDEX](development/EVIDENCE_INDEX.md) → [DECISIONS](development/DECISIONS.md).
4. [CURRENT](CURRENT_PRODUCT_DEVELOPMENT_STATE.md) 최상단 최신 보충만 우선 확인. 1,600줄 누적 역사 전체를 처음부터 읽지 말고 필요한 기능만 검색.
5. 승인 [v1.4.1](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.1_DPS_ONLY_SCOPE_CORRECTION_20261031.md), [v1.4.3](SIMC_SECONDARY_OPTIMIZER_Developer_Notes_v1.4.3_SEASON_GJFO_AUTO_BUILD_APPROVED_20261102.md), [실행 addendum](DEVELOPER_NOTES_ENGINE_FIRST_EXECUTION_ADDENDUM_20261102.md).
6. P2 최신 [실 SimC 전역21→지역6/GP 비교](development/notes/2026-11-10_p2-real-simc-global21-local6-gp-comparison.md) → [실 Native100 중첩11/21 비교](development/notes/2026-11-10_p2-real-simc-nested-11-21-48case-comparison.md) → [v301 중첩 후보 설계](development/notes/2026-11-10_p2-nested11-21-41-real-simc-pilot.md) → [P2 격자·비례 정규화 승인](development/notes/2026-11-10_p2-percentage-grid-proportional-normalization.md) → [P2 신뢰성 정책](development/notes/2026-11-09_p2-opt-reliability-first-open-search-policy.md).
7. 필요한 코드만 확인: `runner/v302_weak_multiregion_zoom.py`, `tests/test_v302_weak_multiregion_zoom.py`, `.github/workflows/offline_focused_continuity.yml`, 기존 `v290/v291`, `v096/v094`, `v292/v293`.
8. 실제 증거는 Actions 원본 [#42757290762](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42757290762), [실 P2 Native 연구 기록](development/notes/2026-11-10_p2-real-simc-global21-local6-gp-comparison.md), [기존 100 Native 영수증](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42752264747), [환경 무이력 Build](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42664089225). 과거 문서의 PENDING을 현재 미구현으로 오판하지 않는다.

## 4. 실제 제품 A~G 상태

| 영역 | 구현/증거 | 미실증 경계 |
|---|---|---|
| A 원본·환경 Build | `v216/v217/v212`; 70783 Ret334 빈 workspace에서 실제 원본→Native3→설치 READY·프로필 PASS [#42664089225](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42664089225) | 다른 미래 시즌 최초 G/J/F/O 자동 구축 및 전체 품질/Policy A 전주기 |
| B 26 DPS | 기본 물리 프로필 26/26 SimC 수용 [#40972829357](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/40972829357) | 모든 전문화/옵션 실제 장기 Native |
| C 보석·영약·기름 | Ret334 G2850/J92/F165/O0/B=T3107, 일반 치가특유 4개·특수 없음 실 Build. O>0 사용자 웹 DPS 별도 [#42598051977](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/42598051977) | 4일반 보석 기본 구성의 실 DPS Native, 타 시즌/일부 선택품목 |
| D Build→사용자 프로필 | `LocalJobs.build_season_environment→v216→v212→load_fresh_profile_for_user` 실제 PASS | 개인 Windows GUI 첫 클릭/실사용 장기 흐름 |
| E G/J/F/O·정책 A | `v222/v220/v196/v212`; B/T 회계·검증 선택지·READY 경로 | 미래 시즌 값/모든 L/E·선택품목 |
| F SimC·탐색·웹 | `v098/v139/v096/v094`, 기본 `v290/v291`, 캐시/재개 `v292/v293`; 26 물리 수용·Native10/캐시 재사용 | 최신 P2 실험 정책은 v291/웹에 미연결. 26 전문화의 품질/전역 최적·사용자 E2E |
| G 운영·증거 | focused CI/ledger, 실제 Native·사용자 웹 증거 각각 보존 | CI PASS를 Native PASS로, internal LocalJobs를 GUI E2E로 확대 금지 |

## 5. 최신 P2 연구와 판단

### 5.1 기존 v301 비교 — 기본 v290 유지

기존 동일 역사 70783 Enhancement 프로필/바이너리 조건에서 v290·중첩11·중첩21 각 48 logical requests, 공유 캐시44, **100 NEW_NATIVE/62.84초**. 320-iteration 최고 확인: v290 **189964.48±315.58**, 중첩11/21 **188379.27±303.00**. 11⊂21⊂41 최종 정수 후보 포함 관계는 구현했지만 해상도 증가가 더 좋은 DPS 발견을 보장하지 않았다. **v290 기본 유지**.

### 5.2 v302 전역21→느슨한 shortlist→여러 지역 m6, GP-UCB 비교

- 실제 입력은 동일 역사 70783 Enhancement Shaman/ilvl334, `B=T=3107`, flask haste165, O0, 특수보석 포함, 고정 SimC 바이너리 SHA `6b83e4d5d2216faf91511fb00ae712cdf4cc0224b0c83107e8c9c7358c24bfc6`. 이는 현재 제품 기본 일반보석4/특수 없음 시나리오가 아니다.
- m21 exact-residual 4방향 후보 19,380개 중 160 scout(35 iterations, 43.03초). 최고 scout 기준 3%+SEM을 **탐색 후보 screening 용도**로 적용해 36개를 남기고 거리 0.08B 이상 떨어진 최대8 지역을 보존. 이는 95% 판정이 아니다.
- 각 지역 m6: 반경 6.5%B에서 12개씩 96 scout → 지역 유력 지점으로 재중심화하고 반경3.25%B에서 8개씩 64 scout → 8개×320 confirmation. **328 NEW_NATIVE / 101.64초**, 320 최고 `(940,1056,1111,0)` **191115.3244±300.5706**. 1000 재확인 최고 `(940,1056,1111,0)` **191038.9411±171.3447**.
- 같은 최초160 scout와 같은 8지역을 공유한 GP-UCB(Matérn GP, SEM을 alpha에 반영)는 추가 local160+8×320; 정확 중복 4개 재사용으로 **164 NEW_NATIVE / 58.41초**. 320 최고 `(1054,1023,1030,0)` **191530.7361±279.4343**. 1000 재확인 중 최고 `(1021,1015,1071,0)` **191428.9084±174.2878**.
- 두 방식의 core 비교는 각각 같은 **13,760 requested iterations**. 6개의 추가 1000-iteration 확인까지 합산한 연구 신규 Native 총계는 기존 기록 기준 **498**(grid328 + GP164 + follow-up checks6). GP와 지역격자의 선택된 1000-iteration 결과 차이 389.97, 독립 근사 pairwise 95% 반폭 약479로 우위 확정 아님. v290 1000 재측정189946.50±166.25보다 높더라도 더 많은 후보/다른 탐색 예산을 썼으므로 알고리즘 우월성 증명은 아니다.
- m41 후보 pool 146,221개 생성 약0.202초는 **수치 후보 생성 측정만**. 41개 기준점으로 실제 SimC Native 탐색은 미실시.
- v302는 `runner/v302_weak_multiregion_zoom.py`의 pure geometry/selector와 오프라인 테스트만 구현. `v291` 실행기·기본 v290·일반 사용자 웹에 연결하지 않았다. GP 연구의 sklearn/scipy는 로컬 연구 스크립트만 사용, 제품 의존성 없음. NOMAD/MADS, TuRBO/STREGO, Sobol, BoTorch noisy acquisition은 조사/비교 후보이지 제품 구현이 아니다.
- 498 Native 연구의 compact script/receipt ZIP SHA는 `7b2e0a80c46bf5a84de84ac2030897a7c12179789cc725b06f67b2800c1cafc5`. ZIP은 과거 대화 첨부였고 GitHub에 바이너리/대량 JSON2를 커밋하지 않았다. 현재 runtime에서 파일을 재확보하지 못했으므로 숫자는 기존 개발 노트/증거 지도 범위로 사용하며 새 채팅에서 재실행하지 않는다.

## 6. 현재 구현·미실증·결함 판정

- **구현 및 실제 제품 범위 PASS:** 70783 한정 무이력 Environment Build/Native3/설치 READY/검증 사용자 프로필, O>0 별도 사용자 웹 DPS, 기본 26 물리 프로필 SimC 수용.
- **오프라인 PASS:** 현재 HEAD #42757290762의 556 tests, 554 PASS/2 SKIP/0 FAIL, ledger PASS.
- **실 Native 연구 PASS(한정):** P2의 역사적 Enhancement 프로필, 고정 바이너리/예산/전투 조건에서 498 Native 탐색 연구. 제품 기본 4보석/특수 없음, 26 DPS 전체, 신규 시즌에 대한 검증은 아님.
- **부분 구현/미연결:** v298/v299/v301/v302 후보 정책과 v291 opt-in/seal 연구는 격리 코드. v302는 selector/geometry만 존재하고 실제 runner 연결·제품 정책 승격 안 됨.
- **미실증:** 미래 신규 시즌 G/J/F/O 최초 구축, 기본 4일반 보석의 DPS Native, 26 전문화 각각의 실제 optimizer 품질, Windows GUI, family-wise 95%/전역 최적, 실 41-grid Native.
- **재현된 제품 결함:** 이번 handoff 조사에서 신규 결함 확인 없음. 초기 #42756858815 실패는 note의 `Changes/Verification` heading 누락으로 ledger가 테스트 전에 차단한 문서 오류였고, #42757010029와 현재 HEAD #42757290762에서 556 tests PASS로 수정 확인.

## 7. 현재 병목과 다음 작업

**핵심 병목은 전역/지역 탐색의 성과에 따라 반경과 Native 예산을 어떻게 배분해야 좋은 고점을 놓치지 않는지**이다. 단순히 21→41로 후보 수를 늘리는 것 자체가 목표가 아니다.

다음 작업 후보(새 채팅은 먼저 읽기 전용 복원 후 사용자 '진행' 전까지 시작 금지):

1. v302/실험 원본 재사용. 동일 global21 scout160과 8개 지역을 기준으로, 각 지역에 최소한의 초기 Native 예산을 균등 배분한다.
2. 지역별 진행률을 관측 DPS 개선량만으로 결정하지 말고, 개선의 지속성·SEM·추가 iterations에서의 순위 변화·지역 내 후보 소진을 함께 고려한다. 초기 shortlist 3%+SEM은 탐색용으로만 유지한다.
3. 개선이 지속되는 지역은 반경을 단계적으로 축소하고 Native 예산을 늘린다. 개선이 멈춘 지역은 반경을 줄이거나 중단해 예산을 재배분하되, 전체 탐색 reserve를 남겨 아직 덜 탐색한 영역을 완전히 제거하지 않는다.
4. fixed local6/equal budget, 성과기반 radius/budget allocation, GP-UCB, MADS-like pattern search, Sobol 초기 표본을 **동일 총 requested iterations + 실제 wall-clock**으로 비교한다. 같은 초기160과 동일 프로필/바이너리/조건을 쓰고 정확 동일 (vector, iterations, binary, profile) 캐시만 재사용한다.
5. 상위 후보는 320/1000 iterations 또는 독립 seed로 별도 확인해 다중 선택편향을 보고한다. 다른 DPS 전문화/경계/스탯비율 조건은 비교 설계가 정리된 뒤 최소 표본으로 확장한다. v302나 GP를 기본 제품에 연결하지 않는다.

### 단기·중기·장기 로드맵

- **단기 P2:** 지역별 성과기반 반경·예산 재분배의 최소 정책 설계 → 동일 Native/iterations/wall-time 비교 → 독립 확인·선택편향/근접 대안 품질 평가.
- **중기 제품 연결:** 검증된 정책만 기존 v291/v096/v094 흐름과 연결; 정확 캐시·취소·재개·95% 적용 범위를 보존하고 일반 사용자 Build→대표 프로필→SimC→결과까지 연결.
- **장기:** 실제 새 시즌에서 G/J/F/O·B/T·정책 A 자동 구축을 같은 엔진으로 갱신하고 26 DPS 전문화의 실제 시나리오를 확장. Windows 사용자 GUI 및 장기 실행 검증. 장비 조합 추천·효과 재구현은 범위 밖.

## 8. 개발 소유권·보호 범위

- 기존 주 제품 개발 채팅이 제품 구현과 일반 사용자 SimC 시험을 계속 소유한다. 이 격리 브랜치는 승인된 P2 실험·개발 지식 기록 용도이며 제품 개발 주도권을 가져오지 않는다.
- 사용자 별도 지시 없이 `main`, immutable `v003`, 원본 `v016`, Project Sources/Instructions UI, Work OS M0/Shared State, 공식 승격을 수정·병합하지 않는다.
- 새 채팅은 첫 응답에서 독립 복원 보고만 하고 STOP한다. 사용자가 별도로 **'진행'**이라고 말하기 전까지 코드·문서 수정, 테스트, 외부 수집, Actions 실행, 고비용 작업, 커밋·병합·공식 승격을 시작하지 않는다.

## 9. 새 채팅 시작 프롬프트

~~~text
SIMC SECONDARY OPTIMIZER 프로젝트를 읽기 전용으로 독립 복원하라.

저장소: degong2-code/simc-secondary-optimizer-runner
격리 브랜치: probe/chat-cache-v035-20261024
복원 기준(인계 작성 직전): isolated e05780ca7e50601b813e6aaf3cbec716d0d282b8 / main 07133e0aaf738d6e4816a6486057b1cd49c018de
최신 단일 인계: docs/CHAT_CONTINUITY_HANDOFF_20261110_P3_HAX_ADAPTIVE_MULTI_REGION_NEXT.md

첫 작업:
1. 격리와 main HEAD를 각각 독립 조회하고 현재 커밋/Actions와 대조한다. 인계 커밋 이후 HEAD가 이동했으면 실제 현재 값을 사용한다.
2. 위 인계 → PRODUCT_CANONICAL_STATUS A~G → PROTOCOL/START_HERE/INDEX/FILE_MAP/EVIDENCE_INDEX/DECISIONS → CURRENT 최상단 → v1.4.1/v1.4.3/Engine-first addendum → 최신 P2 실 Native 노트/코드/영수증 순서로 필요한 범위만 읽는다.
3. 제품 상태와 P2 연구 상태를 분리해 CODE_IMPLEMENTED/OFFLINE_PASS/REAL_NATIVE_PASS/USER_WEB_E2E_PASS/미실증/재현 결함으로 보고한다. 현재 HEAD #42757290762의 556 tests(554 PASS/2 SKIP)와 P2 로컬 Native 498건을 혼동하지 않는다.
4. 현재 우선순위는 v302 global21→loose shortlist→multi-region local6/GP 연구를 재사용해 **지역별 성과에 따른 radius와 Native 예산 자동 조절**을 설계하는 것이다. fixed local6 vs adaptive resource/radius vs GP-UCB/MADS-like/Sobol을 동일 iterations+wall-clock으로 비교하는 설계를 제안한다. v302는 기본 제품/runner 연결 전의 pure selector다.
5. 기존 P2 raw ZIP은 과거 대화 첨부였고 현재 GitHub에 없다. 원본 자료를 확보하지 못하면 수치 영수증을 재사용하고 Native를 반복하지 않는다.

**첫 응답은 읽기 전용 복원 결과만 보고하라.** 프로젝트 최종 목적, 실제 HEAD/main, 최신 승인 정책, A~G 구현·실증 상태, 최근 v302 코드/498 Native 연구, offline CI, 남은 병목, 다음 단계 및 단기·장기 로드맵을 보고한 뒤 즉시 STOP하라.

사용자가 별도로 '진행'이라고 승인하기 전까지 코드/문서 수정, 테스트, Actions 실행, Native SimC, 외부 수집, 파일 변경, 커밋·병합, Project UI/Work OS 변경, 공식 승격을 절대 시작하지 말 것. main·v003·v016·기존 주 제품 개발 채팅 소유권을 보존하라.
~~~
