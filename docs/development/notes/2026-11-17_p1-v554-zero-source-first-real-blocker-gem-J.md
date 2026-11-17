# v554 — 2026-11-17 ZERO-SOURCE→USER-E2E 실제 최초 실행과 J 생산 경계

**검증한 코드:** v552 실제 시험 `e0f69fdc49f97f6c917f23dc1ac80beb69845e4f`; v553 소스 전용 진단 `1b00185f093eb0c1372a1735f2236db70de591cf`.
**저장소/권한:** `degong2-code/simc-secondary-optimizer-runner`, 격리 브랜치 `probe/chat-cache-v035-20261024`만. 개발 주 채팅/Project UI/main/immutable/v016/공식 Work OS 권한 변경 없음.

## 무엇을 실제 실행했나

- 2026-11-17 KST 현재 Retail을 신규 시즌처럼 취급. Windows GitHub Actions 임시 러너에서 **원본 시즌 JSON, `data/current_season_*.json`, `data/season_ordinary_gem_nominal/*.json`, 과거 v202/v206 증거 파일을 시험 코드의 경로에서 격리**. 비어 있는 새 sessions/source/caches를 생성. 오래된 v212 설치·원본 영수증·기존 DPS 캐시는 입력하지 않음.
- `v289`에서 **현재 `12.1.5.70783` 자체 발견**, 동일 게임빌드가 검증된 SimC 공개 바이너리 SHA와 일치할 때만 실행; 새 시즌이라 가정하여 **과거 70783 J92/F165/G2850을 인자로 넘기지 않음**.
- **기존 사용자 경로** `v113.LocalJobs.discover_season_myth_target → build_season_environment → v216/v222/v212`; 성공 시 `v113 sessions/plan→start→result→cache-only`를 사용하도록 시험 정의. 테스트가 새 환경 계산기/SimC solver를 만들지 않음.
- 1회성 [v552 실제 Actions #44031810909](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44031810909), [원본 소형 진단 artifact #14305108654](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44031810909/artifacts/14305108654): **M1 PASS** — 같은 시즌 Wago/공식 source 조인 `CurrencyTypes` ID 3441/3446, 목표 ilvl334, CSV SHA `c1e91e4e17b622136d7c9a37c597cd0fe2409a2f5ccb494659014b154a04ef1f`; `v191/v211/v213` 정상 컴파일, `source_compilation.missing=[]`; 새 환경 Native **3회**, DPS Native **0회**. **M2 BLOCKED** — J 숫자 owner 없음, `v212 environment_ready=false`, 설치되지 않음, 사용자 세션/DPS 미실행. 액션 `failure`는 정상적으로 기록한 최초 블로커이며 full E2E PASS가 아니다.
- 추가 [v553 소스 전용 Actions #44032752995](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44032752995), [진단 artifact #14305663669](https://github.com/degong2-code/simc-secondary-optimizer-runner/actions/runs/44032752995/artifacts/14305663669): 같은 ZERO-SOURCE 계약으로 M1부터 다시 원본 수집, **G/F/DPS Native 0회**. 원본 `v221`의 **보석 75 ItemID**와 기존 `v230` 품질의 join `SAME_BUILD_GEM_ITEM_QUALITY_CANDIDATES_UNADMITTED` **성공(75)**; `v266` 원시 숫자 미확정 **75**; 동일 빌드 `v275/v296` DBC의 **두 양수 Secondary rating 정적 벡터로 분류되는 후보 0/75**, `FOUR_LEADING_CHMV_TYPES_INCOMPLETE`로 pending, `unresolved_item_count=75`. **미관측=0 rating**이나 실제 보석 효과가 없다고 해석 금지. 두 실행의 Wago v161 receipt SHA는 달라서 과거 파일 바이트 동일성을 주장하지 않음.

## 첫 결함과 제품 영향

- **수정 전까지:** 정상 zero-source 기본 환경은 `v216._fresh_pinned_dbc_ordinary_gem_j_source`에서 정적 숫자가 없고, `v548._fresh_four_stat_simc_observed_j_preview`는 서로 다른 `(enchant_id,color_mask,min_ilvl,expansion,quality)` 효과군 **정확히4** 조건을 요구하므로 v221 실제 75 후보에 적용하지 못함. `v551`는 이미 확인된 정적 J를 원래 owner에 전달하는 수치 소비 연결만 완료했으며 **미확정 수치 자체를 생성하지는 않음**.
- **필요한 최소 FIX:** 기존 원본 `v221 ItemID/EnchantID/ExpansionID` + `v230 crafting_quality` + 동일빌드 `v211/v275/v296`의 실제 CHMV **스탯 종류·정확 효과 조건**을 재사용해 확인 가능한 후보를 분류한다. 정적 수치가 없을 때는 기존 `v269/v278` Native 관측으로 **필요한 최상위 후보만 최소/상한 호출**하여 정확한 두 양수 스탯과 합계를 얻고, 승인된 대표스탯별 **제작품질 내림차순→두 rating 합 내림차순→ItemID 오름차순**으로 선택한다. 효과/품질·게임빌드가 증명되지 않은 후보는 PENDING. *효과군 정확히4*라는 선행 가정을 삭제하되 최대 75개 무조건 Native fanout으로 대체하지 않는다.
- 실제 Native가 확정한 숫자도 기존 `v271` 소켓당 J 합산 → 원래 `v216` J source owner/품질·`v232` 소켓 → `v222/v212` 정식 설치까지 연결할 필요가 있다. 새로운 J 예산 엔진, 보석 ItemID collector, SimC 효과/APL/DPS 재구현, 78 신규 Gate 금지.
- **원본 진단이 밝히지 않은 것:** 75개가 각각 왜 정적 벡터 미확정인지(Scaling/0/특수 효과 등의 정확한 분포)는 아직 관측하지 않았음. 따라서 `v296`의 모든 보석이 '스케일링이다'고 확정하지 말고 봉인된 소스의 `source_reason_codes`를 한 번 확인한 뒤 최소 구현/관측 범위 결정. 정상 설치에 미선택 특수보석/5·6 추가 소켓 인증을 강제하지 않는다.

## 실제 상태 및 다음 순서

- **개발 완료 범위:** M1 자동 소스·기본 목표 ilvl **이번 빈 환경 실제 PASS**, v191/v211/v213 컴파일 **실제 PASS**, v221/v230 보석 ItemID+품질 후보 **75 소스 확인**, 초기 환경 Native3, **정식 J/M2/user-E2E PENDING**.
- [v552 코드](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/e0f69fdc49f97f6c917f23dc1ac80beb69845e4f) 및 [v553 Native 0 진단 코드](https://github.com/degong2-code/simc-secondary-optimizer-runner/commit/1b00185f093eb0c1372a1735f2236db70de591cf); 결과의 **실패와 성공을 정확히 분리**한다.
- **다음 최소 작업:** 동일 출처 `v296`의 75건 **미확정 이유 분포·stat-kind 코드**를 소스에서 확인하고, 실제로 식별 가능한 최소 후보들에만 Native 관측 연결; 한 번 측정한 baseline/cases는 SHA별 캐시 재사용. 정상 기본 J가 소스 owner→v212에 도달하면 즉시 같은 제로베이스 실사용 USER DPS·SEM·95%·cache-only까지 재시도. 첫 장애가 바뀌면 그 한 가지에서 다시 STOP→FIX.
- 공식 `15/78 COMPLETE`, `full_product_e2e=PENDING` **변경 없음**. 70783 v524와 v534 성공은 비교할 수 있는 역사 범위 증거이지 v552 시험 입력이나 v552 PASS 근거가 아니다.
